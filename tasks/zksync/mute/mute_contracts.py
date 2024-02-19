from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.utils.helpers import read_json


class MuteContracts(metaclass=Singleton):
    MUTE_ABI = read_json(
        path=('data', 'abis', 'zksync', 'mute','abi.json')
    )
    
    MUTE_UNIVERSAL = RawContract(
        title='Mute',
        address='0x8b791913eb07c32779a16750e3868aa8495f5964',
        abi=MUTE_ABI
    )