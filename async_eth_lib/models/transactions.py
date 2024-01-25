from __future__ import annotations
from typing import TYPE_CHECKING

from web3 import Web3

from .token_amount import TokenAmount

if TYPE_CHECKING:
    from .client import Client


class Transactions:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def get_gas_price(self) -> TokenAmount:
        amount = await self.client.w3.eth.gas_price

        return TokenAmount(amount, wei=True)
    
    async def get_max_priority_fee(self) -> TokenAmount:
        '''
        Get the current max priority fee
        
        Returns:
            Wei: the current max priority fee
        
        '''
        max_priority_fee = await self.client.w3.eth.max_priority_fee
        
        return TokenAmount(max_priority_fee, wei=True)
