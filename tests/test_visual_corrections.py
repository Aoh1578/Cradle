"""Unit tests for visual correction helpers.

Tests _extract_visual_corrections (self_reflection module) and
_inject_visual_corrections (information_gathering module).

Uses importlib to load ONLY the helper functions from source files,
bypassing the heavy cradle.provider import chain (torch, matplotlib, etc.).
"""
import unittest
import importlib.util
import sys
import os
from unittest.mock import MagicMock

# The visual corrections bucket key value (matches cradle/constants.py)
VISUAL_CORRECTIONS_BUCKET = "visual_corrections"

# --- Load helper functions directly from source files -------------------------

def _load_function_from_source(filepath, function_name):
    """Load a single function from a Python source file without triggering
    the full package import chain."""
    spec = importlib.util.spec_from_file_location("_temp_module", filepath)
    module = importlib.util.module_from_spec(spec)

    # Provide minimal stubs for imports the module file needs
    # These are only needed so the module file compiles; the helper functions
    # we test don't actually use them.
    stub = MagicMock()

    originals = {}
    stub_names = [
        "cradle.log", "cradle.config", "cradle.memory",
        "cradle.provider", "cradle.provider.base",
        "cradle.utils.check", "cradle.utils.image_utils",
        "cradle.provider.others", "cradle.provider.others.task_guidance",
    ]
    for name in stub_names:
        originals[name] = sys.modules.get(name)
        sys.modules[name] = stub

    # Ensure cradle.constants is available (lightweight, no heavy deps)
    constants_path = os.path.join(os.path.dirname(__file__), "..", "cradle", "constants.py")
    constants_spec = importlib.util.spec_from_file_location("cradle.constants", constants_path)
    constants_mod = importlib.util.module_from_spec(constants_spec)
    constants_spec.loader.exec_module(constants_mod)
    sys.modules["cradle.constants"] = constants_mod

    # Make cradle package importable
    import cradle
    sys.modules["cradle"] = cradle

    try:
        spec.loader.exec_module(module)
    finally:
        # Restore original modules
        for name in stub_names:
            if originals[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = originals[name]

    return getattr(module, function_name)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_extract_visual_corrections = _load_function_from_source(
    os.path.join(ROOT, "cradle", "provider", "process", "self_reflection.py"),
    "_extract_visual_corrections",
)

_inject_visual_corrections = _load_function_from_source(
    os.path.join(ROOT, "cradle", "provider", "process", "information_gathering.py"),
    "_inject_visual_corrections",
)


def _make_memory(corrections=None):
    """Create a lightweight mock of LocalMemory with a recent_history dict."""
    mem = MagicMock()
    mem.recent_history = {}
    if corrections is not None:
        mem.recent_history[VISUAL_CORRECTIONS_BUCKET] = list(corrections)
    return mem


class TestExtractVisualCorrections(unittest.TestCase):
    """Tests for _extract_visual_corrections."""

    def test_valid_correction_stored(self):
        memory = _make_memory()
        response = {
            "visual_correction": {
                "wrong": "health bar",
                "correct": "mana bar",
                "screen_element": "top-left HUD",
            }
        }

        _extract_visual_corrections(response, memory)

        bucket = memory.recent_history[VISUAL_CORRECTIONS_BUCKET]
        self.assertEqual(len(bucket), 1)
        self.assertEqual(bucket[0]["wrong"], "health bar")
        self.assertEqual(bucket[0]["correct"], "mana bar")
        self.assertEqual(bucket[0]["screen_element"], "top-left HUD")

    def test_null_correction_not_stored(self):
        memory = _make_memory()
        response = {"visual_correction": None}

        _extract_visual_corrections(response, memory)

        self.assertNotIn(VISUAL_CORRECTIONS_BUCKET, memory.recent_history)

    def test_missing_key_not_stored(self):
        memory = _make_memory()
        response = {"reasoning": "all good"}

        _extract_visual_corrections(response, memory)

        self.assertNotIn(VISUAL_CORRECTIONS_BUCKET, memory.recent_history)

    def test_malformed_missing_wrong(self):
        memory = _make_memory()
        response = {
            "visual_correction": {
                "correct": "mana bar",
                "screen_element": "HUD",
            }
        }

        _extract_visual_corrections(response, memory)

        self.assertNotIn(VISUAL_CORRECTIONS_BUCKET, memory.recent_history)

    def test_malformed_missing_correct(self):
        memory = _make_memory()
        response = {
            "visual_correction": {
                "wrong": "health bar",
                "screen_element": "HUD",
            }
        }

        _extract_visual_corrections(response, memory)

        self.assertNotIn(VISUAL_CORRECTIONS_BUCKET, memory.recent_history)

    def test_multiple_corrections_accumulate(self):
        memory = _make_memory()

        for i in range(3):
            response = {
                "visual_correction": {
                    "wrong": f"wrong_{i}",
                    "correct": f"correct_{i}",
                    "screen_element": f"element_{i}",
                }
            }
            _extract_visual_corrections(response, memory)

        bucket = memory.recent_history[VISUAL_CORRECTIONS_BUCKET]
        self.assertEqual(len(bucket), 3)


class TestInjectVisualCorrections(unittest.TestCase):
    """Tests for _inject_visual_corrections."""

    def test_empty_corrections(self):
        memory = _make_memory(corrections=[])
        result = _inject_visual_corrections(memory)
        self.assertEqual(result, {"visual_notes": ""})

    def test_no_bucket_at_all(self):
        memory = _make_memory()
        result = _inject_visual_corrections(memory)
        self.assertEqual(result, {"visual_notes": ""})

    def test_three_corrections(self):
        corrections = [
            {"wrong": "sword", "correct": "staff", "screen_element": "inventory slot 1"},
            {"wrong": "gold", "correct": "silver", "screen_element": "currency display"},
            {"wrong": "night", "correct": "dusk", "screen_element": "sky"},
        ]
        memory = _make_memory(corrections=corrections)

        result = _inject_visual_corrections(memory)
        notes = result["visual_notes"]

        self.assertIn("Visual notes from prior observations", notes)
        self.assertIn("sword", notes)
        self.assertIn("staff", notes)
        self.assertIn("gold", notes)
        self.assertIn("silver", notes)
        self.assertIn("night", notes)
        self.assertIn("dusk", notes)
        self.assertEqual(notes.count("- "), 3)

    def test_max_corrections_limits_output(self):
        corrections = [
            {"wrong": f"wrong_{i}", "correct": f"correct_{i}", "screen_element": f"elem_{i}"}
            for i in range(10)
        ]
        memory = _make_memory(corrections=corrections)

        result = _inject_visual_corrections(memory, max_corrections=5)
        notes = result["visual_notes"]

        # Should only contain the last 5 corrections (indices 5-9)
        for i in range(5):
            self.assertNotIn(f"wrong_{i}", notes)
        for i in range(5, 10):
            self.assertIn(f"wrong_{i}", notes)

        self.assertEqual(notes.count("- "), 5)


if __name__ == "__main__":
    unittest.main()
