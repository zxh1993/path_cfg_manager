import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / 'src' / 'path_cfg_manager' / 'project_path.py'
ENTRY_FILEPATH_ENV_VAR = 'ENTRY-FILEPATH'
PATH_CONFIG_FILENAME = 'path_cfg_manager.json'


def _load_project_path_module(
    entry_filepath: str | None,
    argv0: str,
    home_dir: str | None = None,
):
    spec = importlib.util.spec_from_file_location(
        f'test_project_path_{uuid.uuid4().hex}',
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    original_entry_filepath = os.environ.get(ENTRY_FILEPATH_ENV_VAR)
    original_home = os.environ.get('HOME')
    original_argv0 = sys.argv[0]
    original_sys_path = list(sys.path)
    home_context = tempfile.TemporaryDirectory() if home_dir is None else contextlib.nullcontext(home_dir)

    with home_context as configured_home:
        try:
            os.environ['HOME'] = configured_home
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
            if original_home is None:
                os.environ.pop('HOME', None)
            else:
                os.environ['HOME'] = original_home

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

    def test_user_config_file_can_override_selected_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home_dir = Path(temp_dir) / 'home'
            home_dir.mkdir()
            config_path = home_dir / '.config' / PATH_CONFIG_FILENAME
            config_path.parent.mkdir(parents=True, exist_ok=True)
            shared_data_dir = Path(temp_dir) / 'shared-data'
            config_path.write_text(
                json.dumps(
                    {
                        'data_path': str(shared_data_dir),
                        'logs_path': '~/custom-logs',
                    }
                ),
                encoding='utf-8',
            )

            module = _load_project_path_module(
                entry_filepath=str(MODULE_PATH),
                argv0='/tmp/fallback-project/src/main.py',
                home_dir=str(home_dir),
            )

            self.assertEqual(
                module.relative_data_path('input.csv'),
                str((shared_data_dir / 'input.csv').resolve()),
            )
            self.assertEqual(
                module.relative_logs_path('app.log'),
                str((home_dir / 'custom-logs' / 'app.log').resolve()),
            )
            self.assertEqual(
                module.relative_conf_path('config.json'),
                str((PROJECT_ROOT / 'conf' / 'config.json').resolve()),
            )


if __name__ == '__main__':
    unittest.main()
