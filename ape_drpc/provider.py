from typing import TYPE_CHECKING, cast

from ape.api import UpstreamProvider
from ape_ethereum.provider import Web3Provider
from web3 import HTTPProvider, Web3
from web3.exceptions import ExtraDataLengthError
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware.validation import MAX_EXTRADATA_LENGTH

from .client import DrpcClient

try:
    from web3.middleware import ExtraDataToPOAMiddleware  # type: ignore
except ImportError:
    from web3.middleware import geth_poa_middleware as ExtraDataToPOAMiddleware  # type: ignore

if TYPE_CHECKING:
    from .config import DrpcConfig


class DrpcProvider(Web3Provider, UpstreamProvider, DrpcClient):
    """
    A web3 provider using dRPC caching RPC proxy.

    Docs: https://docs.alchemy.com/alchemy/
    """

    @property
    def config(self) -> "DrpcConfig":
        return cast("DrpcConfig", self.config_manager.get_config("drpc"))

    @property
    def uri(self) -> str:
        if not (
            (networks := self.supported_ecosystems.get(self.network.ecosystem.name))
            and (network := networks.get(self.network.name))
        ):
            raise ValueError(
                f"Unsupported ecosystem/network: {self.network.ecosystem.name}:{self.network.name}"
            )

        uri = f"{str(self.config.host).rstrip('/')}/{network.short_names[0]}"

        if api_key := self.config.api_key:
            return f"{uri}/{api_key}"

        return uri

    @property
    def http_uri(self) -> str:
        # NOTE: Overriding `Web3Provider.http_uri` implementation
        return self.uri

    @property
    def ws_uri(self):
        # NOTE: Overriding `Web3Provider.http_uri` implementation
        return self.uri.replace("https://", "wss://")

    def connect(self):
        self._web3 = Web3(HTTPProvider(self.uri))
        is_poa = None
        try:
            # Any chain that *began* as PoA needs the middleware for pre-merge blocks
            avalanche = 43114
            base = 8453
            optimism = 10
            polygon = 137
            polygon_amoy = 80002

            if self._web3.eth.chain_id in (avalanche, base, optimism, polygon, polygon_amoy):
                self._web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                is_poa = True

            self._web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        except Exception:
            is_poa = None

        if is_poa is None:
            # Check if is PoA but just wasn't as such yet.
            # NOTE: We have to check both earliest and latest
            #   because if the chain was _ever_ PoA, we need
            #   this middleware.
            for option in ("earliest", "latest"):
                try:
                    block = self.web3.eth.get_block(option)  # type: ignore[arg-type]
                except ExtraDataLengthError:
                    is_poa = True
                    break
                else:
                    is_poa = (
                        "proofOfAuthorityData" in block
                        or len(block.get("extraData", "")) > MAX_EXTRADATA_LENGTH
                    )
                    if is_poa:
                        break

            if is_poa and ExtraDataToPOAMiddleware not in self.web3.middleware_onion:
                self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    def disconnect(self):
        self._web3 = None
