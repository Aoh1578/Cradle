"""Pytest conftest: stub out heavy third-party dependencies that are not
available in lightweight CI / test environments.

This must run before any cradle modules are imported.
"""
import sys
import types


def _stub(name, attrs=None):
    """Create a stub module if not already present."""
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)
    mod = sys.modules[name]
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    return mod


# ---------------------------------------------------------------------------
# All third-party packages that cradle transitively imports and are not
# available in the test environment.
# ---------------------------------------------------------------------------

# PIL and all submodules used anywhere in cradle
for sub in ["", ".Image", ".ImageDraw", ".ImageFont", ".ImageChops",
            ".ImageEnhance", ".ImageFilter"]:
    _stub("PIL" + sub)

_stub("PIL.Image", {
    "Image": type("Image", (), {}),
    "open": lambda *a, **kw: None,
    "new": lambda *a, **kw: None,
    "fromarray": lambda *a, **kw: None,
})

# numpy
_stub("numpy", {
    "ndarray": type("ndarray", (), {}),
    "array": lambda *a, **kw: None,
    "zeros": lambda *a, **kw: None,
    "uint8": int,
    "float32": float,
    "float64": float,
    "int32": int,
    "int64": int,
    "mean": lambda *a, **kw: 0,
    "sum": lambda *a, **kw: 0,
    "abs": lambda *a, **kw: None,
    "clip": lambda *a, **kw: None,
    "where": lambda *a, **kw: None,
    "stack": lambda *a, **kw: None,
    "concatenate": lambda *a, **kw: None,
})
_stub("numpy.linalg")

# cv2
_stub("cv2", {
    "imread": lambda *a, **kw: None,
    "imwrite": lambda *a, **kw: None,
    "resize": lambda *a, **kw: None,
    "cvtColor": lambda *a, **kw: None,
    "INTER_NEAREST": 0,
    "INTER_LINEAR": 1,
    "COLOR_BGR2RGB": 4,
    "COLOR_RGB2BGR": 5,
    "COLOR_BGR2GRAY": 6,
    "VideoCapture": type("VideoCapture", (), {}),
    "VideoWriter": type("VideoWriter", (), {}),
    "VideoWriter_fourcc": lambda *a: 0,
})

# torch
for sub in ["", ".nn", ".nn.functional", ".cuda", ".utils", ".utils.data"]:
    _stub("torch" + sub)
_stub("torch", {"device": lambda *a: None, "no_grad": lambda: (lambda fn: fn),
                 "tensor": lambda *a, **kw: None, "Tensor": type("Tensor", (), {})})

# torchvision
for sub in ["", ".ops", ".transforms"]:
    _stub("torchvision" + sub)
_stub("torchvision.ops", {"box_convert": lambda *a, **kw: None})

# psutil
_stub("psutil", {
    "cpu_percent": lambda *a, **kw: 0.0,
    "virtual_memory": lambda: type("VM", (), {"percent": 0.0})(),
    "Process": type("Process", (), {}),
})

# openai
_stub("openai", {
    "OpenAI": type("OpenAI", (), {}),
    "AzureOpenAI": type("AzureOpenAI", (), {}),
    "APIError": type("APIError", (Exception,), {}),
    "RateLimitError": type("RateLimitError", (Exception,), {}),
    "APITimeoutError": type("APITimeoutError", (Exception,), {}),
})

# anthropic
_stub("anthropic", {
    "Anthropic": type("Anthropic", (), {}),
    "RateLimitError": type("RateLimitError", (Exception,), {}),
    "APIError": type("APIError", (Exception,), {}),
    "APITimeoutError": type("APITimeoutError", (Exception,), {}),
})

# backoff
_stub("backoff", {
    "on_exception": lambda *a, **kw: (lambda fn: fn),
})

# tiktoken
_stub("tiktoken", {
    "encoding_for_model": lambda *a, **kw: None,
})

# dotenv
_stub("dotenv", {
    "load_dotenv": lambda *a, **kw: None,
})

# matplotlib
_stub("matplotlib")
_stub("matplotlib.pyplot", {
    "subplots": lambda *a, **kw: (None, None),
    "show": lambda *a, **kw: None,
    "savefig": lambda *a, **kw: None,
})
_stub("matplotlib.patches")

# scipy
_stub("scipy")
_stub("scipy.ndimage", {"binary_fill_holes": lambda *a, **kw: None})

# segment_anything
_stub("segment_anything", {
    "SamPredictor": type("SamPredictor", (), {}),
    "sam_model_registry": {},
    "SamAutomaticMaskGenerator": type("SamAutomaticMaskGenerator", (), {}),
})
for sub in [".modeling", ".modeling.sam", ".utils", ".utils.transforms"]:
    _stub("segment_anything" + sub)

# groundingdino
_stub("groundingdino")
_stub("groundingdino.util")
_stub("groundingdino.util.inference", {"load_image": None, "load_model": None})

# supervision
_stub("supervision")

# easyocr
_stub("easyocr")

# mss, pyautogui, pydirectinput
_stub("mss")
_stub("pyautogui")
_stub("pydirectinput")

# spacy
_stub("spacy")

# dill
_stub("dill")

# dataclass_wizard
_dcw = _stub("dataclass_wizard", {
    "JSONWizard": type("JSONWizard", (), {}),
})
_dcw.__path__ = []  # make it look like a package
_stub("dataclass_wizard.abstractions", {
    "W": type("W", (), {}),
})
_stub("dataclass_wizard.type_def", {
    "JSONObject": type("JSONObject", (), {}),
    "Encoder": type("Encoder", (), {}),
})

# ahk / AHK
_stub("ahk", {"AHK": type("AHK", (), {})})

# win32 (Windows-only)
_stub("win32gui")
_stub("win32process")

# colorama
# colorama — needs to return "" for any attribute (Fore.RED, Back.WHITE, etc.)
class _ColorStub:
    def __getattr__(self, name):
        return ""

_stub("colorama", {
    "Fore": _ColorStub(),
    "Back": _ColorStub(),
    "Style": _ColorStub(),
    "init": lambda *a, **kw: None,
})
