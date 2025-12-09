from functools import cache

import requests
import yaml
from ape.types import HexInt
from ape.utils.basemodel import ManagerAccessMixin
from pydantic import BaseModel, Field

CHAIN_META_URL = "https://raw.githubusercontent.com/drpcorg/public/refs/heads/main/chains.yaml"


class ChainSettings(BaseModel):
    mev_critical: bool = Field(alias="mev-critical", default=False)


class ChainMeta(BaseModel):
    id: str
    code: str
    chain_id: HexInt = Field(alias="chain-id")

    short_names: list[str] = Field(alias="short-names")
    settings: ChainSettings = ChainSettings()

    grpc_id: int = Field(alias="grpcId")


class DrpcClient(ManagerAccessMixin):
    @classmethod
    @cache
    def get_supported_ecosystems(cls) -> dict[str, dict[str, ChainMeta]]:
        if (response := requests.get(CHAIN_META_URL)).status_code >= 400:
            response.raise_for_status()

        return {
            ecosystem.name: {
                network.name: chain
                for chain in map(ChainMeta.model_validate, protocol["chains"])
                # NOTE: Check that dRPC-supported network is in Ape's network list
                if (network := ecosystem.networks.get(chain.id.lower()))
                and network.chain_id == chain.chain_id
            }
            for protocol in yaml.safe_load(response.text)["chain-settings"]["protocols"]
            if protocol["type"] in ("eth",)
            # NOTE: Check that dRPC-supported ecosystem is in Ape's ecosystem list
            and (ecosystem := cls.network_manager.ecosystems.get(protocol["id"]))
        }

    @property
    def supported_ecosystems(self) -> dict[str, dict[str, ChainMeta]]:
        return self.__class__.get_supported_ecosystems()
