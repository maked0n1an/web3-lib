from typing import (
    Optional, 
    Tuple
)
import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.bridges.bridge_data import TokenBridgeInfo
from tasks.layer_zero._data.models import LayerZeroNetworkData
from tasks.layer_zero.coredao.coredao_contracts import CoreDaoBridgeContracts
from tasks.layer_zero.stargate.stargate_contracts import StargateContracts
from tasks.layer_zero.testnet_bridge.testnet_bridge_contracts import TestnetBridgeContracts


class LayerZeroData(Singleton):
    projects = {
        'stargate': {
            Networks.Arbitrum.name: LayerZeroNetworkData(
                chain_id=110,
                bridge_dict={
                    CurrencySymbol.USDC_E: TokenBridgeInfo(
                        bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                        pool_id=1
                    ),
                    CurrencySymbol.USDT: TokenBridgeInfo(
                        bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                        pool_id=2
                    ),
                    CurrencySymbol.DAI: TokenBridgeInfo(
                        bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                        pool_id=3
                    ),
                    CurrencySymbol.ETH: TokenBridgeInfo(
                        bridge_contract=StargateContracts.ARBITRUM_ETH,
                        pool_id=13
                    )
                }
            ),
            Networks.Avalanche.name: LayerZeroNetworkData(
                chain_id=106,
                bridge_dict={
                    CurrencySymbol.USDC: TokenBridgeInfo(
                        bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                        pool_id=1
                    ),
                    CurrencySymbol.USDT: TokenBridgeInfo(
                        bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                        pool_id=2
                    ),
                }
            ),
            Networks.BSC.name: LayerZeroNetworkData(
                chain_id=102,
                bridge_dict={
                    CurrencySymbol.USDT: TokenBridgeInfo(
                        bridge_contract=StargateContracts.BSC_USDT,
                        pool_id=2
                    ),
                    CurrencySymbol.BUSD: TokenBridgeInfo(
                        bridge_contract=StargateContracts.BSC_BUSD,
                        pool_id=5
                    )
                }
            ),
            Networks.Fantom.name: LayerZeroNetworkData(
                chain_id=112,
                bridge_dict={
                    CurrencySymbol.USDC: TokenBridgeInfo(
                        bridge_contract=StargateContracts.FANTOM_USDC,
                        pool_id=21
                    )
                }
            ),
            Networks.Optimism.name: LayerZeroNetworkData(
                chain_id=111,
                bridge_dict={
                    CurrencySymbol.USDC_E: TokenBridgeInfo(
                        bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                        pool_id=1
                    ),
                    CurrencySymbol.DAI: TokenBridgeInfo(
                        bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                        pool_id=3
                    ),
                    CurrencySymbol.ETH: TokenBridgeInfo(
                        bridge_contract=StargateContracts.OPTIMISM_ETH,
                        pool_id=13
                    )
                }
            ),
            Networks.Polygon.name: LayerZeroNetworkData(
                chain_id=109,
                bridge_dict={
                    CurrencySymbol.USDC_E: TokenBridgeInfo(
                        bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                        pool_id=1
                    ),
                    CurrencySymbol.USDT: TokenBridgeInfo(
                        bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                        pool_id=2
                    ),
                    CurrencySymbol.DAI: TokenBridgeInfo(
                        bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                        pool_id=3
                    )
                }
            )
        },
        'coredaobridge': {
            Networks.BSC.name: LayerZeroNetworkData(
                chain_id=102,
                bridge_dict={
                    CurrencySymbol.USDT: TokenBridgeInfo(
                        bridge_contract=CoreDaoBridgeContracts.BSC
                    )
                }
            )
        },
        'testnetbridge': {
            Networks.Arbitrum.name: LayerZeroNetworkData(
                chain_id=110,
                bridge_dict={
                    CurrencySymbol.GETH_LZ: TokenBridgeInfo(
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
        network_data = cls.get_network_data(
            project=project, network=network
        )

        return network_data.chain_id

    @classmethod
    def get_pool_id(
        cls,
        project: str,
        network: str,
        token_ticker: str
    ) -> int | None:
        token_bridge_info = cls.get_token_bridge_info(
            project=project, network=network, token_ticker=token_ticker
        )

        return token_bridge_info.pool_id
    
    @classmethod
    def get_chain_id_and_pool_id(
        cls,
        project: str,
        network: str,
        token_ticker: str
    ) -> Tuple[int, Optional[int]]:
        token_ticker = token_ticker.upper()
        
        network_data = cls.get_network_data(
            project=project, network=network
        )

        cls._check_for_bridge_contract(
            token=token_ticker, bridge_dict=network_data.bridge_dict
        )
        
        chain_id = network_data.chain_id
        pool_id = network_data.bridge_dict[token_ticker].pool_id
        
        return (chain_id, pool_id)

    @classmethod
    def get_token_bridge_info(
        cls,
        project: str,
        network: str,
        token_ticker: str
    ) -> TokenBridgeInfo:
        token_ticker = token_ticker.upper()

        network_data = cls.get_network_data(
            project=project, network=network
        )

        cls._check_for_bridge_contract(
            token=token_ticker, bridge_dict=network_data.bridge_dict
        )

        token_bridge_info = network_data.bridge_dict[token_ticker]
        return token_bridge_info

    @classmethod
    def get_network_data(
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
    
    def _check_for_bridge_contract(
        token: str,
        bridge_dict: dict[str, TokenBridgeInfo]
    ) -> None:
        if token not in bridge_dict:
            raise exceptions.ContractNotExists(
                f"The bridge contract for {token} has not been added "
                f"to {__class__.__name__} bridge contracts"
            )

