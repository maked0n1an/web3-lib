from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .account_manager import AccountManager
from .default_abis import DefaultAbis
from .token_amount import TokenAmount


class Contracts:
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager

    async def get_balance(
        self,
        token_address: str | ChecksumAddress | None = None,
        address: str | ChecksumAddress | None = None,
        decimals: int = 18
    ) -> TokenAmount:
        if not address:
            address = self.account_manager.address

        address = Web3.to_checksum_address(address)

        if token_address:
            contract = await self.default_token(contract_address=token_address)

            amount = await contract.functions.balanceOf(address).call()
            decimals = await contract.functions.decimals().call()
        else:
            amount = await self.account_manager.w3.eth.get_balance(account=address)

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def default_token(self, contract_address: ChecksumAddress | str) -> Contract | AsyncContract:
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.account_manager.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract
