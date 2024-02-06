from typing import (
    Type,
    Union
)

from web3 import types
from web3.contract import AsyncContract, Contract

from async_eth_lib.models.contracts.raw_contract import (
    NativeTokenContract,
    RawContract,
    TokenContract
)
from .token_amount import TokenAmount


class ParamsTypes:
    Contract = RawContract | AsyncContract
    TokenContract = TokenContract | NativeTokenContract
    Address = str | types.Address | types.ChecksumAddress | types.ENS
    Amount = float | int | TokenAmount
    GasPrice = float | int | TokenAmount
    GasLimit = int | TokenAmount
