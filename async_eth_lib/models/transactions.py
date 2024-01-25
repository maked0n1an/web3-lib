from web3.types import TxReceipt, _Hash32, TxParams

from .account import Account
from .token_amount import TokenAmount


class Transactions:
    def __init__(self, account: Account) -> None:
        self.account = account

    async def get_gas_price(self) -> TokenAmount:
        '''
        Get the current gas price

        Return:
            Wei            
        '''
        amount = await self.account.w3.eth.gas_price

        return TokenAmount(amount, wei=True)

    async def get_max_priority_fee(self) -> TokenAmount:
        """Get the current max priority fee

        Returns:
            Wei: the current max priority fee
        """
        max_priority_fee = await self.account.w3.eth.max_priority_fee

        return TokenAmount(max_priority_fee, wei=True)

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        gas_price = await self.account.w3.eth.estimate_gas(transaction=tx_params)
        
        return TokenAmount(gas_price, wei=True)
