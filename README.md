# path_cfg_manager

A lightweight Python package that auto-detects your project root directory and provides convenience functions for accessing common subdirectories (`data/`, `models/`, `conf/`, `logs/`).

## How It Works

On import, `path_cfg_manager` determines the project root by:

1. Checking the `ENTRY-FILEPATH` environment variable, or
2. Locating the `/src/` segment in `sys.argv[0]` and using the parent as the project root.

It then automatically adds `<project_root>/src` to `sys.path`.

`ENTRY-FILEPATH` is parsed with the same logic as `sys.argv[0]`, so it should point
to a file path under `<project_root>/src/`.

## Installation

```bash
pip install path_cfg_manager
```

Or install from source:

```bash
pip install .
```

## Usage

```python
from path_cfg_manager import relative_data_path, relative_conf_path, local_config

# Get absolute path to a file in the data/ directory
csv_path = relative_data_path('input', 'data.csv')

# Get absolute path to a file in the conf/ directory
cfg_path = relative_conf_path('settings.yaml')

# Load and cache a JSON config from conf/
config = local_config('config.json')
```

## API Reference

### Path Functions

All path functions accept `*args` path components and return an absolute path.

| Function | Base directory |
|---|---|
| `relative_project_path(*args)` | Project root |
| `relative_data_path(*args)` | `<project>/data/` |
| `relative_models_path(*args)` | `<project>/models/` |
| `relative_conf_path(*args)` | `<project>/conf/` |
| `relative_logs_path(*args)` | `<project>/logs/` |

### `local_config(config_name='config.json') -> dict`

Loads a JSON file from the `conf/` directory and caches it. Subsequent calls with the same filename return the cached result.

## License

MIT
