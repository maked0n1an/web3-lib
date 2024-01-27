from web3 import types
from web3.contract import AsyncContract

from .token_amount import TokenAmount
from ..contracts.raw_contract import RawContract


class ParamsTypes:
    Contract = str | types.Address | types.ChecksumAddress | types.ENS | RawContract | AsyncContract
    Address = str | types.Address | types.ChecksumAddress | types.ENS
    Amount = float | int | TokenAmount
    GasPrice = int | TokenAmount
    GasLimit = int | TokenAmount
