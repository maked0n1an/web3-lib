from async_eth_lib.models.bridges.bridge_data import TokenBridgeInfo
from async_eth_lib.models.bridges.network_data import NetworkData
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.layer_zero.coredao.coredao_contracts import CoreDaoBridgeContracts


class CoredaoData(NetworkDataFetcher, metaclass=Singleton):
    networks_data = {
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                CurrencySymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.BSC
                )
            }
        )
    }
