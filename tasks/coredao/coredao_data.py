from async_eth_lib.models.contracts.contracts import TokenContracts
import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from data.models import (
    BridgeData,
    LayerZeroNetworkInfo
)
from tasks.coredao.coredao_contracts import CoreDaoBridgeContracts


class CoreDaoBridgeData(Singleton):
    networks_dict = {
        Networks.BSC.name: LayerZeroNetworkInfo(
            chain_id=102,
            token_dict={
                CurrencySymbol.USDT: BridgeData(
                    token_contract=TokenContracts.BSC_USDT,
                    bridge_contract=CoreDaoBridgeContracts.BSC
                )
            }
        )
    }

    @classmethod
    def get_token(
        cls, 
        network: str, 
        token: str
    ) -> BridgeData | None:
        network = network.lower()
        token = token.upper()

        if network not in cls.networks_dict:
            raise exceptions.NetworkNotAdded(
                f"The requested network has not been "
                f"added to {cls.__name__} networks dict"
            )

        network_data = cls.networks_dict[network]
        if token not in network_data.token_dict:
            raise exceptions.ContractNotExists(
                f"This contract has not been added "
                f"to {cls.__name__} token contracts"
            )

        return network_data.token_dict[token]
