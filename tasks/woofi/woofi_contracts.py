from async_eth_lib.models.dexes.dex_info import DexInfo
import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.utils.helpers import read_json


class WoofiContracts(Singleton):
    WOOFI_ROUTER_V2_ABI = read_json(
        path=('data', 'abis', 'woofi', 'abi.json')
    )
    
    contracts_dict={
        'WooRouterV2': {
            Networks.Arbitrum.name: RawContract(
                title='WooRouterV2_Arbitrum',
                address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                abi=WOOFI_ROUTER_V2_ABI
            ),
            Networks.Polygon.name: RawContract(
                title='WooRouterV2_Polygon',
                address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                abi=WOOFI_ROUTER_V2_ABI
            )
        }
    }
    
    @classmethod
    def get_dex_contract(cls, name: str, network: str) -> RawContract | None:
        
        if name in cls.contracts_dict:
            router_data = cls.contracts_dict[name]

            if network in router_data:
                return router_data[network]

        return None