from eth_typing import ChecksumAddress
from web3.types import (
    TxParams
)
from eth_account.datastructures import (
    SignedTransaction
)

from ..account.account_manager import AccountManager
from ..others.token_amount import TokenAmount
from .tx import Tx


class Transaction:
    def __init__(self, account_manager: AccountManager) -> None:
        self.account_manager = account_manager

    @staticmethod
    async def decode_input_data():
        pass

    async def get_nonce(self, address: ChecksumAddress | None = None) -> int:
        if not address:
            address = self.account_manager.account.address

        nonce = await self.account_manager.w3.eth.get_transaction_count(address)
        return nonce

    async def get_gas_price(self) -> TokenAmount:
        """
        Get the current gas price

        Return:
            Wei 

        """
        amount = await self.account_manager.w3.eth.gas_price

        return TokenAmount(
            amount,
            decimals=self.account_manager.network.decimals,
            wei=True
        )

    async def get_max_priority_fee(self) -> TokenAmount:
        """
        Get the current max priority fee

        Returns:
            Wei: the current max priority fee

        """
        max_priority_fee = await self.account_manager.w3.eth.max_priority_fee

        return TokenAmount(
            max_priority_fee,
            decimals=self.account_manager.network.decimals,
            wei=True
        )

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Wei: the estimate gas.

        """
        gas_price = await self.account_manager.w3.eth.estimate_gas(transaction=tx_params)

        return TokenAmount(
            gas_price,
            decimals=self.account_manager.network.decimals,
            wei=True
        )

    async def auto_add_params(self, tx_params: TxParams) -> TxParams:
        """
        Add 'chainId', 'nonce', 'from', 'gasPrice' or 'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to
            transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            TxParams: parameters of the transaction with added values.

        """
        if 'chainId' not in tx_params:
            tx_params['chainId'] = self.account_manager.network.chain_id

        if not tx_params.get('nonce'):
            tx_params['nonce'] = await self.get_nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.account_manager.account.address

        is_eip_1559_tx_type = self.account_manager.network.tx_type == 2
        current_gas_price = await self.get_gas_price()

        if is_eip_1559_tx_type:
            if 'gasPrice' in tx_params:
                tx_params['maxFeePerGas'] = tx_params['gasPrice']
                del tx_params['gasPrice']
            else:
                tx_params['maxFeePerGas'] = current_gas_price.Wei

        elif 'gasPrice' not in tx_params:
            tx_params['gasPrice'] = current_gas_price.Wei

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (await self.get_max_priority_fee()).Wei
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas']

        if not tx_params.get('gas') or not int(tx_params['gas']):
            tx_params['gas'] = (await self.get_estimate_gas(tx_params=tx_params)).Wei

        return tx_params

    async def sign_transaction(self, tx_params: TxParams) -> SignedTransaction:
        """
        Sign a transaction.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            SignedTransaction: the signed transaction.

        """
        signed_tx = self.account_manager.account.sign_transaction(
            transaction_dict=tx_params)

        return signed_tx

    async def sign_message(self, message: str):
        pass

    async def sign_and_send(self, tx_params: TxParams) -> Tx:
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.

        """
        tx_params = await self.auto_add_params(tx_params)
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.account_manager.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

        return Tx(tx_hash=tx_hash, params=tx_params)
