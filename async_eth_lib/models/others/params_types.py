from web3 import types
from web3.contract import AsyncContract

from async_eth_lib.models.contracts.raw_contract import RawContract
from .token_amount import TokenAmount

class ParamsTypes:
    Contract = str | types.Address | types.ChecksumAddress | types.ENS | RawContract | AsyncContract
    Address = str | types.Address | types.ChecksumAddress | types.ENS
    Amount = float | int | TokenAmount
    GasPrice = float | int | TokenAmount 
    GasLimit = int | TokenAmount
