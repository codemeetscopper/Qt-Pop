# Sample Plugin

Sample plugin to do nothing

## Author

Aby

## Installation

Drop the `sample_plugin/` directory into Nova's `plugins/` folder, then restart
Nova or use **Plugins → Import Plugin** to load a `.zip` archive.

## Plugin structure

```
sample_plugin/
├── plugin.json     Manifest (required)
├── plugin_main.py  Plugin entry class (required)
├── README.md       This file (optional)
└── resources/      Static assets (optional)
```

## Permissions

| Permission | Description |
|------------|-------------|
| `ipc`      | Communicate with the Nova host via local socket |
