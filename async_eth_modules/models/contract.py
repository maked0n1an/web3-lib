from __future__ import annotations
from typing import TYPE_CHECKING

from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .defaul_abis import DefaultAbis
if TYPE_CHECKING:
    from .client import Client


class Contract:
    def __init__(self, client: Client):
        self.client = client

    def default_token(self, contract_address: ChecksumAddress | str) -> Contract | AsyncContract:
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.client.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract
