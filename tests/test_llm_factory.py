"""Unit tests for LLMFactory routing logic.

Tests _detect_provider_type which is the core routing decision function.
The actual provider instantiation is not tested here (requires heavy deps).
"""
import unittest
import importlib.util
import sys
import os
from unittest.mock import MagicMock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_factory():
    """Load just the LLMFactory class with minimal stubs."""
    # Stub all heavy deps — including parent packages to prevent __init__.py
    # from pulling in the full provider tree.
    for mod_name in [
        "cradle.provider", "cradle.provider.llm",
        "cradle.provider.llm.openai", "cradle.provider.llm.restful_claude",
        "cradle.utils",
    ]:
        if mod_name not in sys.modules:
            sys.modules[mod_name] = MagicMock()

    # json_utils and file_utils need load_json and assemble_project_path
    # to raise exceptions for string paths (so fallback routing triggers)
    json_utils_mock = MagicMock()
    json_utils_mock.load_json = MagicMock(side_effect=FileNotFoundError("stubbed"))
    sys.modules["cradle.utils.json_utils"] = json_utils_mock

    file_utils_mock = MagicMock()
    file_utils_mock.assemble_project_path = lambda p: p  # pass-through
    sys.modules["cradle.utils.file_utils"] = file_utils_mock

    # We need the real Singleton
    singleton_path = os.path.join(ROOT, "cradle", "utils", "singleton.py")
    singleton_spec = importlib.util.spec_from_file_location("cradle.utils.singleton", singleton_path)
    singleton_mod = importlib.util.module_from_spec(singleton_spec)
    singleton_spec.loader.exec_module(singleton_mod)
    sys.modules["cradle.utils.singleton"] = singleton_mod

    # Patch cradle.utils to have the real Singleton
    sys.modules["cradle.utils"].Singleton = singleton_mod.Singleton

    # Load the factory
    factory_path = os.path.join(ROOT, "cradle", "provider", "llm", "llm_factory.py")
    spec = importlib.util.spec_from_file_location("cradle.provider.llm.llm_factory", factory_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LLMFactory, singleton_mod.Singleton


LLMFactory, Singleton = _load_factory()


class TestDetectProviderType(unittest.TestCase):
    """Tests for LLMFactory._detect_provider_type."""

    def setUp(self):
        Singleton._instances.pop(LLMFactory, None)

    def tearDown(self):
        Singleton._instances.pop(LLMFactory, None)

    def test_reads_provider_type_from_dict(self):
        factory = LLMFactory()
        self.assertEqual(
            factory._detect_provider_type({"provider_type": "openai_compat"}),
            "openai_compat",
        )

    def test_reads_claude_from_dict(self):
        factory = LLMFactory()
        self.assertEqual(
            factory._detect_provider_type({"provider_type": "claude"}),
            "claude",
        )

    def test_reads_openai_from_dict(self):
        factory = LLMFactory()
        self.assertEqual(
            factory._detect_provider_type({"provider_type": "openai"}),
            "openai",
        )

    def test_fallback_filename_openai(self):
        factory = LLMFactory()
        result = factory._detect_provider_type("conf/openai_config.json")
        self.assertEqual(result, "openai")

    def test_fallback_filename_claude(self):
        factory = LLMFactory()
        result = factory._detect_provider_type("conf/claude_config.json")
        self.assertEqual(result, "claude")

    def test_fallback_unknown_defaults_to_openai(self):
        factory = LLMFactory()
        result = factory._detect_provider_type("conf/some_random_thing.json")
        self.assertEqual(result, "openai")

    def test_dict_without_provider_type_defaults_to_openai(self):
        factory = LLMFactory()
        result = factory._detect_provider_type({"comp_model": "gpt-4"})
        self.assertEqual(result, "openai")


if __name__ == "__main__":
    unittest.main()
