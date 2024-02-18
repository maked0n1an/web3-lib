from async_eth_lib.models.bridges.bridge_data import TokenBridgeInfo
from async_eth_lib.models.bridges.network_data import NetworkData
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.layer_zero.testnet_bridge.testnet_bridge_contracts import TestnetBridgeContracts


class TestnetBridgeData(NetworkDataFetcher, Singleton):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                CurrencySymbol.GETH_LZ: TokenBridgeInfo(
                    bridge_contract=TestnetBridgeContracts.ARBITRUM_GETH_LZ,
                )
            }
        )
    }
