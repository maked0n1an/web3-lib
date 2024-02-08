from typing import (
    Optional, 
    Tuple
)
import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.contracts.contracts import TokenContracts
from tasks.layer_zero._data.models import LayerZeroNetworkData
from async_eth_lib.models.bridges.bridge_data import BridgeData
from tasks.layer_zero.coredao.coredao_contracts import CoreDaoBridgeContracts
from tasks.layer_zero.stargate.stargate_contracts import StargateContracts
from tasks.layer_zero.testnet_bridge.testnet_bridge_contracts import TestnetBridgeContracts


class LayerZeroData(Singleton):
    projects = {
        'stargate': {
            Networks.Arbitrum.name: LayerZeroNetworkData(
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
            Networks.Avalanche.name: LayerZeroNetworkData(
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
            Networks.BSC.name: LayerZeroNetworkData(
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
            Networks.Fantom.name: LayerZeroNetworkData(
                chain_id=112,
                token_dict={
                    CurrencySymbol.USDC: BridgeData(
                        token_contract=TokenContracts.FANTOM_USDC,
                        bridge_contract=StargateContracts.FANTOM_USDC,
                        pool_id=21
                    )
                }
            ),
            Networks.Optimism.name: LayerZeroNetworkData(
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
            Networks.Polygon.name: LayerZeroNetworkData(
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
        },
        'coredaobridge': {
            Networks.BSC.name: LayerZeroNetworkData(
                chain_id=102,
                token_dict={
                    CurrencySymbol.USDT: BridgeData(
                        token_contract=TokenContracts.BSC_USDT,
                        bridge_contract=CoreDaoBridgeContracts.BSC
                    )
                }
            )
        },
        'testnetbridge': {
            Networks.Arbitrum.name: LayerZeroNetworkData(
                chain_id=110,
                token_dict={
                    CurrencySymbol.GETH: BridgeData(
                        token_contract=TokenContracts.ARBITRUM_GETH_LZ,
                        bridge_contract=TestnetBridgeContracts.ARBITRUM_GETH_LZ,
                    )
                }
            )
        }
    }

    @classmethod
    def get_chain_id(
        cls,
        project: str,
        network: str
    ) -> int | None:
        network_data = cls._get_network_data(
            project=project, network=network
        )

        return network_data.chain_id

    @classmethod
    def get_pool_id(
        cls,
        project: str,
        network: str,
        token: str
    ) -> int | None:
        token_data = cls.get_token(
            project=project, network=network, token=token
        )

        return token_data.pool_id
    
    @classmethod
    def get_chain_id_and_pool_id(
        cls,
        project: str,
        network: str,
        token: str
    ) -> Tuple[int, Optional[int]]:
        token = token.upper()
        
        network_data = cls._get_network_data(
            project=project, network=network
        )

        cls._check_for_token(token=token, token_dict=network_data.token_dict)
        
        chain_id = network_data.chain_id
        pool_id = network_data.token_dict[token].pool_id
        
        return (chain_id, pool_id)

    @classmethod
    def get_token(
        cls,
        project: str,
        network: str,
        token: str
    ) -> BridgeData:
        token = token.upper()

        network_data = cls._get_network_data(
            project=project, network=network
        )

        cls._check_for_token(token=token, token_dict=network_data.token_dict)

        token_data = network_data.token_dict[token]
        return token_data

    @classmethod
    def _get_network_data(
        cls,
        project: str,
        network: str
    ) -> LayerZeroNetworkData:
        project = project.lower()
        network = network.lower()

        if project not in cls.projects:
            raise exceptions.DexNotExists(
                f"The '{project.capitalize()}' project has not been "
                f"added to {__class__.__name__} class"
            )

        networks = cls.projects[project]

        if network not in networks:
            raise exceptions.NetworkNotAdded(
                f"The '{network.capitalize()}' network has not been "
                f"added to {__class__.__name__} networks dict"
            )

        network_data = networks[network]

        return network_data
    
    def _check_for_token(
        token: str,
        token_dict: dict[str, BridgeData]
    ) -> None:
        if token not in token_dict:
            raise exceptions.ContractNotExists(
                f"The {token} contract has not been added "
                f"to {__class__.__name__} token contracts"
            )

