from datetime import datetime, timedelta, timezone

import pytest

from ape_drpc.provider import DrpcProvider

# Ecosystems that routinely fail on free/public dRPC (paid-only, dead, or flaky).
SKIP = [
    "berachain",
    "blast",
    "celo",
    "cronos",
    "filecoin",
    "kroma",
    "moonbeam",
    "polygon-zkevm",  # public tip ~months stale
    "shibarium",  # free-plan gated
    "soneium",  # eth_blockNumber unavailable on free
    "sophon",
    "taiko",
    "zksync",
]

# Per-network skips inside otherwise-healthy ecosystems.
NETWORK_SKIPS = {
    "ethereum": {"holesky"},  # sunset; public tip months stale
    "scroll": {"sepolia"},  # free-plan gated
    "sei": {"testnet"},  # eth_blockNumber unavailable on free
}


@pytest.fixture(autouse=True)
def use_public_drpc(monkeypatch):
    """Prefer public *.drpc.org so CI exercises the plugin without a paid plan."""
    monkeypatch.delenv("APE_DRPC_API_KEY", raising=False)


@pytest.mark.parametrize(
    "ecosystem", (e for e in DrpcProvider.get_supported_ecosystems() if e not in SKIP)
)
def test_connection(networks, ecosystem):
    network_skips = NETWORK_SKIPS.get(ecosystem, set())
    supported = DrpcProvider.get_supported_ecosystems()[ecosystem]
    tested = 0
    for network in supported:
        if network in network_skips:
            continue
        choice = f"{ecosystem}:{network}:drpc"
        try:
            with networks.parse_network_choice(choice) as provider:
                assert isinstance(provider, DrpcProvider)
                assert abs(
                    provider.get_block("latest").datetime - datetime.now(timezone.utc)
                ) < timedelta(minutes=5)
                tested += 1
        except Exception as err:
            msg = str(err).lower()
            if any(
                needle in msg
                for needle in (
                    "not available on free plan",
                    "does not exist/is not available",
                    "upgrade to paid plan",
                    "block not found",
                    "rate limit",
                )
            ):
                pytest.skip(f"{choice}: {err}")
            raise

    if tested == 0:
        pytest.skip(f"no free/public networks left to exercise for {ecosystem}")
