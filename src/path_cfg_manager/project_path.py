import os
import sys
import json

ENTRY_FILEPATH_ENV_VAR = 'ENTRY_FILEPATH'
ENTRY_FILEPATH_ENV_VAR_COMPATIBLE = 'ENTRY-FILEPATH'
PATH_CONFIG_FILENAME = 'path_cfg_manager.json'


class _PathObject:
    project_path: str | None = None
    data_path: str | None = None
    models_path: str | None = None
    conf_path: str | None = None
    logs_path: str | None = None


def _set_sub_paths(project_path: str) -> None:
    """Set all subdirectory paths from the given project root."""
    _PathObject.project_path = project_path
    _PathObject.data_path = os.path.join(project_path, 'data')
    _PathObject.models_path = os.path.join(project_path, 'models')
    _PathObject.conf_path = os.path.join(project_path, 'conf')
    _PathObject.logs_path = os.path.join(project_path, 'logs')


def _apply_user_path_config() -> None:
    """Override default subdirectory paths from ~/.config/path_cfg_manager.json when present."""
    config_path = os.path.expanduser(os.path.join('~', '.config', PATH_CONFIG_FILENAME))
    if not os.path.isfile(config_path):
        return

    with open(config_path, encoding='utf-8') as f:
        path_dict = json.load(f)

    data_path = path_dict.get('data_path')
    if data_path is not None:
        _PathObject.data_path = os.path.expanduser(data_path)

    models_path = path_dict.get('models_path')
    if models_path is not None:
        _PathObject.models_path = os.path.expanduser(models_path)

    conf_path = path_dict.get('conf_path')
    if conf_path is not None:
        _PathObject.conf_path = os.path.expanduser(conf_path)

    logs_path = path_dict.get('logs_path')
    if logs_path is not None:
        _PathObject.logs_path = os.path.expanduser(logs_path)


def _entry_file_path() -> str:
    """Return the configured entry filepath, falling back to ``sys.argv[0]``."""
    return os.getenv(ENTRY_FILEPATH_ENV_VAR) or os.getenv(ENTRY_FILEPATH_ENV_VAR_COMPATIBLE) or sys.argv[0]


def _project_path_from_entry(entry_file_path: str) -> str | None:
    """Resolve a project root from an entry filepath using the ``/src/`` marker."""
    file_path = os.path.realpath(entry_file_path)
    index = file_path.find(f'{os.sep}src{os.sep}')
    if index == -1:
        return None
    return file_path[:index]


def __init_path() -> None:
    project_path = _project_path_from_entry(_entry_file_path())
    if project_path is None:
        print('/src/ directory not found in path. Path initialization failed.')
        return
    sys.path.append(os.path.join(project_path, 'src'))
    _set_sub_paths(project_path)
    _apply_user_path_config()
    print('PROJECT_PATH=' + _PathObject.project_path)


__init_path()


def relative_project_path(*args: str) -> str:
    """Return an absolute path relative to the project root.

    Args:
        *args: Path components to join after the project root.
    """
    assert _PathObject.project_path is not None, "Project path not initialized"
    return os.path.realpath(os.path.join(_PathObject.project_path, *args))


def relative_data_path(*args: str) -> str:
    """Return an absolute path relative to the ``data/`` directory.

    Args:
        *args: Path components to join after the data directory.
    """
    assert _PathObject.project_path is not None, "Project path not initialized"
    return os.path.realpath(os.path.join(_PathObject.data_path, *args))


def relative_conf_path(*args: str) -> str:
    """Return an absolute path relative to the ``conf/`` directory.

    Args:
        *args: Path components to join after the conf directory.
    """
    assert _PathObject.project_path is not None, "Project path not initialized"
    return os.path.realpath(os.path.join(_PathObject.conf_path, *args))


def relative_models_path(*args: str) -> str:
    """Return an absolute path relative to the ``models/`` directory.

    Args:
        *args: Path components to join after the models directory.
    """
    assert _PathObject.project_path is not None, "Project path not initialized"
    return os.path.realpath(os.path.join(_PathObject.models_path, *args))


def relative_logs_path(*args: str) -> str:
    """Return an absolute path relative to the ``logs/`` directory.

    Args:
        *args: Path components to join after the logs directory.
    """
    assert _PathObject.project_path is not None, "Project path not initialized"
    return os.path.realpath(os.path.join(_PathObject.logs_path, *args))


_config_dict: dict[str, dict] = {}


def local_config(config_name: str = 'config.json') -> dict:
    """Load and cache a JSON config file from the ``conf/`` directory.

    Args:
        config_name: Filename of the config file (default ``config.json``).

    Returns:
        Parsed JSON content as a dict.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    config = _config_dict.get(config_name)
    if config is None:
        try:
            with open(relative_conf_path(config_name)) as f:
                config = json.load(f)
                _config_dict[config_name] = config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file '{config_name}' not found in conf directory")
    return config


__all__ = [
    'relative_project_path',
    'relative_data_path',
    'relative_conf_path',
    'relative_models_path',
    'relative_logs_path',
    'local_config',
]
