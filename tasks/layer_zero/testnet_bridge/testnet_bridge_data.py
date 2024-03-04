from async_eth_lib.models.bridges.bridge_data import TokenBridgeInfo
from async_eth_lib.models.bridges.network_data import NetworkData
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.layer_zero.testnet_bridge.testnet_bridge_contracts import TestnetBridgeContracts


class TestnetBridgeData(NetworkDataFetcher):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.GETH_LZ: TokenBridgeInfo(
                    bridge_contract=TestnetBridgeContracts.ARBITRUM_GETH_LZ,
                )
            }
        )
    }
