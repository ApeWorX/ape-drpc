from datetime import datetime, timedelta, timezone

import pytest

from ape_drpc.provider import DrpcProvider

# NOTE: These cause problems but ostensibly work sometimes
SKIP = [
    "berachain",
    "blast",
    "celo",
    "cronos",
    "filecoin",
    "kroma",
    "moonbeam",
    "sophon",
    "taiko",
    "zksync",
]


@pytest.mark.parametrize(
    "ecosystem", (e for e in DrpcProvider.get_supported_ecosystems() if e not in SKIP)
)
def test_connection(networks, ecosystem):
    for network in DrpcProvider.get_supported_ecosystems()[ecosystem]:
        with networks.parse_network_choice(f"{ecosystem}:{network}:drpc") as provider:
            assert isinstance(provider, DrpcProvider)
            assert abs(
                provider.get_block("latest").datetime - datetime.now(timezone.utc)
            ) < timedelta(minutes=5)
