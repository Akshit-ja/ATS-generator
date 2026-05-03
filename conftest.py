import os
from pathlib import Path


REPO_ROOT = Path(__file__).parent.resolve()
INTEGRATION_TESTS_DIR = (REPO_ROOT / "tests").resolve()
BACKEND_INTEGRATION_DIR = (REPO_ROOT / "backend" / "tests" / "integration").resolve()
OPENAI_CHECK_TEST = (REPO_ROOT / "backend" / "test_api_key.py").resolve()
SCRIPTS_DIR = (REPO_ROOT / "scripts").resolve()

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("DISABLE_TELEMETRY", "true")


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def pytest_ignore_collect(path, config):
    path = Path(str(path)).resolve()

    if path == OPENAI_CHECK_TEST and not _env_flag("RUN_OPENAI_TESTS"):
        return True

    if INTEGRATION_TESTS_DIR in path.parents or path == INTEGRATION_TESTS_DIR:
        return not _env_flag("RUN_INTEGRATION_TESTS")

    if BACKEND_INTEGRATION_DIR in path.parents or path == BACKEND_INTEGRATION_DIR:
        return not _env_flag("RUN_INTEGRATION_TESTS")

    if SCRIPTS_DIR in path.parents or path == SCRIPTS_DIR:
        return not _env_flag("RUN_SCRIPT_TESTS")

    return False
