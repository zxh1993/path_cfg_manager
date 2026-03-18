"""path_cfg_manager - Project path and configuration management utility.

Automatically detects the project root directory by locating the /src/ segment in
``ENTRY-FILEPATH`` or, when that variable is unset, ``sys.argv[0]``.

On import, the package appends ``<project_root>/src`` to ``sys.path``, so any
modules under the project's ``src/`` directory become importable without manual
PYTHONPATH configuration.

Functions:
    relative_project_path(*args)  - Return an absolute path relative to the project root.
    relative_data_path(*args)     - Return an absolute path relative to the data/ directory.
    relative_conf_path(*args)     - Return an absolute path relative to the conf/ directory.
    relative_models_path(*args)   - Return an absolute path relative to the models/ directory.
    relative_logs_path(*args)     - Return an absolute path relative to the logs/ directory.
    local_config(config_name)     - Load and cache a JSON config file from the conf/ directory.

Example:
    >>> from path_cfg_manager import relative_data_path, local_config
    >>> relative_data_path('input', 'file.csv')
    '/your/project/data/input/file.csv'
    >>> local_config('db.json')
    {'host': 'localhost', 'port': 3306}
"""

from path_cfg_manager.project_path import (
    relative_project_path,
    relative_data_path,
    relative_conf_path,
    relative_models_path,
    relative_logs_path,
    local_config,
)

__all__ = [
    'relative_project_path',
    'relative_data_path',
    'relative_conf_path',
    'relative_models_path',
    'relative_logs_path',
    'local_config',
]
