from .account import Account
from .token_amount import TokenAmount

class Transactions:
    def __init__(self, account: Account) -> None:
        self.account = account

    async def get_gas_price(self) -> TokenAmount:
        amount = await self.account.w3.eth.gas_price

        return TokenAmount(amount, wei=True)
    
    async def get_max_priority_fee(self) -> TokenAmount:
        '''
        Get the current max priority fee
        
        Returns:
            Wei: the current max priority fee
        
        '''
        max_priority_fee = await self.account.w3.eth.max_priority_fee
        
        return TokenAmount(max_priority_fee, wei=True)
