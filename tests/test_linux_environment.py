import platform
import sys


def test_python_version_supported():
    assert sys.version_info >= (3, 12)


def test_codespace_runner_is_linux():
    assert platform.system() == "Linux"


def test_runtime_architecture_is_detected():
    assert platform.machine()
