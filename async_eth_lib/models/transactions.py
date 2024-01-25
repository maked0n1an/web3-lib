from web3.types import TxReceipt, _Hash32, TxParams

from .account import Account
from .token_amount import TokenAmount


class Transactions:
    def __init__(self, account: Account) -> None:
        self.account = account

    async def get_gas_price(self) -> TokenAmount:
        """
        Get the current gas price

        Return:
            Wei            
        """
        amount = await self.account.w3.eth.gas_price

        return TokenAmount(amount, wei=True)

    async def get_max_priority_fee(self) -> TokenAmount:
        """
        Get the current max priority fee

        Returns:
            Wei: the current max priority fee
        """
        max_priority_fee = await self.account.w3.eth.max_priority_fee

        return TokenAmount(max_priority_fee, wei=True)

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        gas_price = await self.account.w3.eth.estimate_gas(transaction=tx_params)
        
        return TokenAmount(gas_price, wei=True)
    
    async def auto_add_params(self, tx_params: TxParams) -> TxParams:
        if not tx_params['chainId']:
            tx_params['chainId'] = self.account.network.chain_id
        
        if not tx_params['nonce']:
            tx_params['nonce'] = self.account.get_nonce()
            
        if not tx_params['from']:
            tx_params['from'] = self.account.address
        
        if not tx_params['gasPrice'] and not tx_params['maxFeePerGas']:
            gas_price = (await self.get_gas_price()).Wei
            
            if self.account.network.tx_type == 2:
                tx_params['maxFeePerGas'] = gas_price
            else:
                tx_params['gasPrice'] = gas_price
        elif tx_params['gasPrice'] and not int(tx_params['gasPrice']):
            tx_params['gasPrice'] = (await self.get_gas_price()).Wei
            
        if tx_params['maxFeePerGas'] and not tx_params['maxPriorityFeePerGas']:
            tx_params['maxPriorityFeePerGas'] = (await self.get_max_priority_fee()).Wei
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas']
        
        if not tx_params['gas'] or not int(tx_params['gas']):
            tx_params['gas'] = (await self.get_estimate_gas(tx_params=tx_params)).Wei
        
        return tx_params
