# Quick Start

<a href="https://drpc.org?ref=4b8b1e">
  <img style="width:218px;height:54px" src="https://drpc.org/images/external/powered-by-drpc-dark.svg" alt="Powered by dRPC" />
</a>

Ape plugin for [dRPC](https://drpc.org?ref=4b8b1e)

## Dependencies

- [python3](https://www.python.org/downloads) version 3.10 up to 3.13.

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-drpc
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-drpc.git
cd ape-drpc
python3 setup.py install
```

## Quick Usage

Configure via `ape-config.yaml`:

```yaml
drpc:
  host: https://my-drpc.domain...
  api_key: "..." # NOTE: Omit if you don't have one
```

or `pyproject.toml`

```toml
[tool.ape.drpc]
host = "https://my-drpc.domain..."
api_key = "..."  # NOTE: Omit if you don't have one
```

and then launch using any network combo your drpc instance supports via `--network <eco>:<net>:drpc`

```{note}
You can also use `APE_DRPC_HOST=...` and `APE_DRPC_API_KEY=...` to set config via environment variables
```

## Development

Please see the [contributing guide](CONTRIBUTING.md) to learn more how to contribute to this project.
Comments, questions, criticisms and pull requests are welcomed.
