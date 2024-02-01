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
                    title='WooFi_Arbitrum',
                    address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                    abi=read_json(
                        path=('data', 'abis', 'woofi', 'abi.json')
                    )
                ),
                Networks.Polygon.name: RawContract(
                    title='Woofi_Polygon',
                    address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                    abi=read_json(
                        path=('data', 'abis', 'woofi', 'abi.json')
                    )
                )
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
