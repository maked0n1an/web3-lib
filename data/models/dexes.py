import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.dexes.dex_info import DexInfo
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.utils.helpers import read_json


class Dexes(Singleton):
    WOOFI = DexInfo(
        contracts_dict={
            'WooRouterV2': {
                Networks.Arbitrum.name: RawContract(
                    title='WooRouterV2_Arbitrum',
                    address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                    abi=read_json(
                        path=('data', 'abis', 'woofi', 'abi.json')
                    )
                ),
                Networks.Polygon.name: RawContract(
                    title='WooRouterV2_Polygon',
                    address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                    abi=read_json(
                        path=('data', 'abis', 'woofi', 'abi.json')
                    )
                )
            }
        }
    )

    STARGATE = DexInfo(
        contracts_dict={
            'USDC': {
                Networks.Arbitrum.name: RawContract(
                    title='StargateFinanceRouter_Arbitrum_USDC',
                    address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                    abi=read_json(
                        path=('data', 'abis', 'stargate', 'abi.json')
                    )
                ),
                Networks.Avalanche.name: RawContract(
                    title='StargateFinanceRouter_Avalanche_USDC',
                    address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    abi=read_json(
                        path=('data', 'abis', 'stargate', 'abi.json')
                    )
                ),
                Networks.Polygon.name: RawContract(
                    title='StargateFinanceRouter_Polygon_USDC',
                    address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    abi=read_json(
                        path=('data', 'abis', 'stargate', 'abi.json')
                    )
                ),
            }
        }
    )

    @staticmethod
    def get_dex(dex_name: str) -> DexInfo:
        dex_name = dex_name.upper()
        dex = getattr(Dexes, dex_name, None)

        if dex is None:
            raise exceptions.DexNotExists(
                "This DEX has not been added to Contracts")

        return dex
