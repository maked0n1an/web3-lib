import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.contracts.contracts import TokenContracts
from data.models import (
    LayerZeroNetworkInfo, 
    BridgeData
)
from tasks.stargate.stargate_contracts import StargateContracts


class StargateData(Singleton):
    networks_dict = {
        Networks.Arbitrum.name: LayerZeroNetworkInfo(
            chain_id=110,
            token_dict={
                CurrencySymbol.USDC: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_USDC,
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=1
                ),
                CurrencySymbol.USDT: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_USDT,
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=2
                ),
                CurrencySymbol.DAI: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_DAI,
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=3
                ),
                CurrencySymbol.ETH: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_ETH,
                    bridge_contract=StargateContracts.ARBITRUM_ETH,
                    pool_id=13
                )
            }
        ),
        Networks.Avalanche.name: LayerZeroNetworkInfo(
            chain_id=106,
            token_dict={
                CurrencySymbol.USDC: BridgeData(
                    token_contract=TokenContracts.AVALANCHE_USDC,
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=1
                ),
                CurrencySymbol.USDT: BridgeData(
                    token_contract=TokenContracts.AVALANCHE_USDT,
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=2
                ),
            }
        ),
        Networks.BSC.name: LayerZeroNetworkInfo(
            chain_id=102,
            token_dict={
                CurrencySymbol.USDT: BridgeData(
                    token_contract=TokenContracts.BSC_USDT,
                    bridge_contract=StargateContracts.BSC_USDT,
                    pool_id=2
                ),
                CurrencySymbol.BUSD: BridgeData(
                    token_contract=TokenContracts.BSC_BUSD,
                    bridge_contract=StargateContracts.BSC_BUSD,
                    pool_id=5
                )
            }
        ),
        Networks.Fantom.name: LayerZeroNetworkInfo(
            chain_id=112,
            token_dict={
                CurrencySymbol.USDC: BridgeData(
                    token_contract=TokenContracts.FANTOM_USDC,
                    bridge_contract=StargateContracts.FANTOM_USDC,
                    pool_id=21
                )
            }
        ),
        Networks.Optimism.name: LayerZeroNetworkInfo(
            chain_id=111,
            token_dict={
                CurrencySymbol.USDC: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_USDC,
                    bridge_contract='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
                    pool_id=1
                ),
                CurrencySymbol.DAI: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_DAI,
                    bridge_contract='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
                    pool_id=3
                ),
                CurrencySymbol.ETH: BridgeData(
                    token_contract=TokenContracts.ARBITRUM_ETH,
                    bridge_contract='0xb49c4e680174e331cb0a7ff3ab58afc9738d5f8b',
                    pool_id=13
                )
            }
        ),
        Networks.Polygon.name: LayerZeroNetworkInfo(
            chain_id=109,
            token_dict={                
                CurrencySymbol.USDC_e: BridgeData(
                    token_contract=TokenContracts.POLYGON_USDC_E,
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=1
                ),
                CurrencySymbol.USDT: BridgeData(
                    token_contract=TokenContracts.POLYGON_USDT,
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=2
                ),
                CurrencySymbol.DAI: BridgeData(
                    token_contract=TokenContracts.POLYGON_DAI,
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=3
                )
            }
        )
    }

    @classmethod
    def get_chain_id(cls, network: str) -> int | None:
        if network not in cls.networks_dict:
            raise exceptions.NetworkNotAdded(
                f"The requested network has not been "
                f"added to StargateData networks dict"
            )
        return cls.networks_dict[network].chain_id
    
    @classmethod
    def get_pool_id(
        cls, 
        network: str,
        token: str
    ) -> int | None:
        bridge_data = cls.get_token(network=network, token=token)
        
        return bridge_data.pool_id

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
                f"added to StargateData networks dict"
            )

        network_data = cls.networks_dict[network]
        if token not in network_data.token_dict:
            raise exceptions.ContractNotExists(
                f"This contract has not been added "
                f"to StargateData token contracts"
            )

        return network_data.token_dict[token]
