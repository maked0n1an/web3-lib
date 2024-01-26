from async_eth_lib.models.contract import RawContract
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.dataclasses import DefaultAbis
from async_eth_lib.utils.helpers import read_json


class Contracts(Singleton):
    ARBITRUM_WOOFI = RawContract(
        title="WooFi",
        address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
        abi=read_json(path=('data', 'abis', 'woofi.json'))
    )

    ARBITRUM_USDC = RawContract(
        title='USDC',
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        abi=DefaultAbis.Token
    )

    ARBITRUM_ETH = RawContract(
        title='ETH',
        address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        abi=DefaultAbis.Token
    )