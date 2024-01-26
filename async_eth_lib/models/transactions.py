from typing import Any

from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3.types import (
    TxReceipt,
    _Hash32,
    TxParams,
)
from eth_account.datastructures import (
    SignedTransaction,
    SignedMessage
)

from .classes import AutoRepr
from .account_manager import AccountManager
from .token_amount import TokenAmount
import async_eth_lib.utils.exceptions as exceptions


class Tx(AutoRepr):
    """
    An instance of transaction for easy execution of actions on it.

    Attributes:
        hash (Optional[_Hash32]): a transaction hash.
        params (Optional[dict]): the transaction parameters.
        receipt (Optional[TxReceipt]): a transaction receipt.
        function_identifier (Optional[str]): a function identifier.
        input_data (Optional[Dict[str, Any]]): an input data.

    """
    hash: _Hash32 | None
    params: dict | None
    receipt: TxReceipt | None
    function_identifier: str | None
    input_data: dict[str, Any] | None

    def __init__(
        self,
        tx_hash: str | _Hash32 | None = None,
        params: dict | None = None
    ) -> None:
        """
        Initialize the class.

        Args:
            tx_hash (Optional[Union[str, _Hash32]]): the transaction hash. (None)
            params (Optional[dict]): a dictionary with transaction parameters. (None)

        """
        if not tx_hash and not params:
            raise exceptions.TransactionException(
                "Specify 'tx_hash' or 'params' argument values!")

        if isinstance(tx_hash, str):
            tx_hash = HexBytes(tx_hash)

        self.hash = tx_hash
        self.params = params
        self.receipt = None
        self.function_identifier = None
        self.input_data = None

    async def parse_params(self, account_manager: AccountManager) -> dict[str, Any]:
        """
        Parse the parameters of a sent transaction.

        Args:
            account_manager (AccountManager): the AccountManager instance.

        Returns:
            Dict[str, Any]: the parameters of a sent transaction.

        """
        tx_data = await account_manager.w3.eth.get_transaction(transaction_hash=self.hash)
        self.params = {
            'chainId': account_manager.network.chain_id,
            'nonce': int(tx_data.get('nonce')),
            'gasPrice': int(tx_data.get('gasPrice')),
            'gas': int(tx_data.get('gas')),
            'from': tx_data.get('from'),
            'to': tx_data.get('to'),
            'data': tx_data.get('input'),
            'value': int(tx_data.get('value'))
        }

        return self.params
    
    async def wait_for_transaction_receipt(
        self,
        account_manager: AccountManager,
        timeout: int | float = 120, 
        poll_latency: float = 0.1
    ) -> dict[str, Any]: 
        """
        Wait for the transaction receipt.

        Args:
            account_manager (AccountManager): the AccountManager instance.
            timeout (Union[int, float]): the receipt waiting timeout. (120 sec)
            poll_latency (float): the poll latency. (0.1 sec)

        Returns:
            Dict[str, Any]: the transaction receipt.

        """
        self.receipt = dict(await account_manager.w3.eth.wait_for_transaction_receipt(
            transaction_hash=self.hash, timeout=timeout, poll_latency=poll_latency
        ))
        
        return self.receipt

    async def 

class Transactions:
    def __init__(self, account_manager: AccountManager) -> None:
        self.account_manager = account_manager

    async def get_gas_price(self) -> TokenAmount:
        """
        Get the current gas price

        Return:
            Wei 

        """
        amount = await self.account_manager.w3.eth.gas_price

        return TokenAmount(amount, wei=True)

    async def get_max_priority_fee(self) -> TokenAmount:
        """
        Get the current max priority fee

        Returns:
            Wei: the current max priority fee

        """
        max_priority_fee = await self.account_manager.w3.eth.max_priority_fee

        return TokenAmount(max_priority_fee, wei=True)

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Wei: the estimate gas.

        """
        gas_price = await self.account_manager.w3.eth.estimate_gas(transaction=tx_params)

        return TokenAmount(gas_price, wei=True)

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

        if 'nonce' not in tx_params:
            tx_params['nonce'] = self.account_manager.w3.eth.get_transaction_count(
                self.account_manager.account.address)

        if 'from' not in tx_params:
            tx_params['from'] = self.account_manager.account.address

        gas_price = (await self.get_gas_price()).Wei

        if 'gasPrice' not in tx_params and 'maxFeePerGas' not in tx_params:
            tx_params['maxFeePerGas' if self.account_manager.network.tx_type ==
                      2 else 'gasPrice'] = gas_price
        elif 'gasPrice' in tx_params and not int(tx_params['gasPrice']):
            tx_params['gasPrice'] = gas_price

        if 'maxFeePerGas' not in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (await self.get_max_priority_fee()).Wei
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas']

        if 'gas' not in tx_params or not int(tx_params['gas']):
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

    async def sign_and_send(self, tx_params: TxParams):
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.

        """
        await self.auto_add_params(tx_params)
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.account_manager.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

        return Tx(tx_hash=tx_hash, params=tx_params)
