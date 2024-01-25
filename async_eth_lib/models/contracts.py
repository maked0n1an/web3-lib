from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .default_abis import DefaultAbis
from .account import Account


class Contracts:
    def __init__(self, account: Account):
        self.account = account

    async def default_token(self, contract_address: ChecksumAddress | str) -> Contract | AsyncContract:
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.account.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract
