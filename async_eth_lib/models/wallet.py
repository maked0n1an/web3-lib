from __future__ import annotations
from typing import TYPE_CHECKING

from eth_typing import ChecksumAddress
from web3 import Web3

from async_eth_lib.models.token_amount import TokenAmount

if TYPE_CHECKING:
    from .client import Client


class Wallet:
    def __init__(self, client: Client):
        self.client = client

    async def get_balance(
        self,
        token_address: str | ChecksumAddress | None = None,
        address: str | ChecksumAddress | None = None,
        decimals: int = 18
    ) -> None:
        if not address:
            address = self.client.account.address

        address = Web3.to_checksum_address(address)

        if not token_address:
            amount = await self.client.w3.eth.get_balance(account=address)
        else:
            token_address = Web3.to_checksum_address(token_address)
            contract = await self.client.contracts.default_token(contract_address=token_address)

            amount = await contract.functions.balanceOf(address).call()
            decimals = await contract.functions.decimals().call

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def get_nonce(self, address: str | ChecksumAddress | None = None) -> int:
        if not address:
            address = self.client.account.address
        nonce = await self.client.w3.eth.get_transaction_count(address)

        return nonce
