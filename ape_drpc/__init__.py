from ape import plugins


@plugins.register(plugins.Config)
def config_class():
    from .config import DrpcConfig

    return DrpcConfig


@plugins.register(plugins.ProviderPlugin)
def providers():
    from .provider import DrpcProvider

    supported_ecosystems = DrpcProvider.get_supported_ecosystems()
    for ecosystem_name, supported_networks in supported_ecosystems.items():
        for network_name in supported_networks:
            yield ecosystem_name, network_name, DrpcProvider
