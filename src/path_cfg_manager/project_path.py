import os
import sys
import json


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


def __init_path() -> None:
    project_path = os.getenv('PROJECTPATH')
    if project_path is None:
        file_path = os.path.realpath(sys.argv[0])
        index = file_path.find(f'{os.sep}src{os.sep}')
        if index == -1:
            print('PROJECTPATH env var not set and /src/ directory not found in path. Path initialization failed.')
            return
        project_path = file_path[:index]
    sys.path.append(os.path.join(project_path, 'src'))
    _set_sub_paths(project_path)
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
