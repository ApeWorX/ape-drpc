from ape.api import PluginConfig
from pydantic import AnyUrl
from pydantic_settings import SettingsConfigDict


class DrpcConfig(PluginConfig):
    # NOTE: dRPC NodeCloud instance
    host: AnyUrl = AnyUrl("https://lb.drpc.live")
    api_key: str | None = None

    model_config = SettingsConfigDict(env_prefix="APE_DRPC_")
