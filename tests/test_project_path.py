import contextlib
import importlib.util
import io
import os
import sys
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / 'src' / 'path_cfg_manager' / 'project_path.py'
ENTRY_FILEPATH_ENV_VAR = 'ENTRY-FILEPATH'


def _load_project_path_module(entry_filepath: str | None, argv0: str):
    spec = importlib.util.spec_from_file_location(
        f'test_project_path_{uuid.uuid4().hex}',
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    original_entry_filepath = os.environ.get(ENTRY_FILEPATH_ENV_VAR)
    original_argv0 = sys.argv[0]
    original_sys_path = list(sys.path)

    try:
        if entry_filepath is None:
            os.environ.pop(ENTRY_FILEPATH_ENV_VAR, None)
        else:
            os.environ[ENTRY_FILEPATH_ENV_VAR] = entry_filepath
        sys.argv[0] = argv0
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    finally:
        sys.argv[0] = original_argv0
        sys.path[:] = original_sys_path
        if original_entry_filepath is None:
            os.environ.pop(ENTRY_FILEPATH_ENV_VAR, None)
        else:
            os.environ[ENTRY_FILEPATH_ENV_VAR] = original_entry_filepath

    return module


class ProjectPathTests(unittest.TestCase):
    def test_entry_filepath_env_has_priority_over_sys_argv_zero(self) -> None:
        module = _load_project_path_module(
            entry_filepath=str(MODULE_PATH),
            argv0='/tmp/fallback-project/src/main.py',
        )

        self.assertEqual(module._PathObject.project_path, str(PROJECT_ROOT))

    def test_sys_argv_zero_is_used_when_entry_filepath_is_missing(self) -> None:
        module = _load_project_path_module(
            entry_filepath=None,
            argv0=str(PROJECT_ROOT / 'src' / 'runner.py'),
        )

        self.assertEqual(module._PathObject.project_path, str(PROJECT_ROOT))

    def test_project_path_from_entry_requires_src_segment(self) -> None:
        module = _load_project_path_module(
            entry_filepath=str(MODULE_PATH),
            argv0='/tmp/fallback-project/src/main.py',
        )

        self.assertIsNone(module._project_path_from_entry('/tmp/not-a-project/main.py'))


if __name__ == '__main__':
    unittest.main()
