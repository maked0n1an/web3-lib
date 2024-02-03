from web3 import Web3
from web3.contract import Contract, AsyncContract
from web3.types import TxParams
from eth_typing import ChecksumAddress

from async_eth_lib.models.account.account_manager import AccountManager
from async_eth_lib.models.others.dataclasses import CommonValues, DefaultAbis
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.transactions.transaction import Transaction
from async_eth_lib.models.transactions.tx import Tx
from async_eth_lib.models.transactions.tx_args import TxArgs

from async_eth_lib.utils.helpers import (
    make_request, 
    text_between
)
from .raw_contract import RawContract


class Contract:
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager
        self.transaction = Transaction(account_manager)

    @staticmethod
    async def get_signature(hex_signature: str) -> list | None:
        """
        Find all matching signatures in the database of https://www.4byte.directory/.

        :param str hex_signature: a signature hash.
        :return list | None: matches found.
        """
        try:
            url = f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}'
            response = await make_request(method="GET", url=url)
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]
        except:
            return

    @staticmethod
    async def parse_function(text_signature: str) -> dict:
        """
        Construct a function dictionary for the Application Binary Interface (ABI) based on the provided text signature.

        :param str text_signature: a text signature, e.g. approve(address,uint256).
        :return dict: the function dictionary for the ABI.
        """
        name, sign = text_signature.split('(', 1)
        sign = sign[:-1]
        tuples = []
        while '(' in sign:
            tuple_ = text_between(text=sign[:-1], begin='(', end=')')
            tuples.append(tuple_.split(',') or [])
            sign = sign.replace(f'({tuple_})', 'tuple')

        inputs = sign.split(',')
        if inputs == ['']:
            inputs = []

        function = {
            'type': 'function',
            'name': name,
            'inputs': [],
            'outputs': [{'type': 'uint256'}]
        }
        i = 0
        for type_ in inputs:
            input_ = {'type': type_}
            if type_ == 'tuple':
                input_['components'] = [{'type': comp_type}
                                        for comp_type in tuples[i]]
                i += 1

            function['inputs'].append(input_)

        return function

    @staticmethod
    async def get_contract_attributes(contract: ParamsTypes.Contract) -> tuple[ChecksumAddress, list | None]:
        """
        Convert different types of contract to its address and ABI.
        Args:
            contract (ParamsTypes.Contract): the contract address or instance

        Returns:
            tuple[ChecksumAddress, list | None]: the checksummed contract address and ABI.
        """
        abi = None
        address = contract
        if isinstance(contract, (AsyncContract, RawContract)):
            address, abi = contract.address, contract.abi
        return Web3.to_checksum_address(address), abi

    async def approve(
        self,
        token: ParamsTypes.Contract,
        spender: ParamsTypes.Address,
        amount: ParamsTypes.Amount | None = None,
        gas_price: ParamsTypes.GasPrice | None = None,
        gas_limit: ParamsTypes.GasLimit | None = None,
        nonce: int | None = None,
        is_approve_infinity: bool = False
    ) -> Tx:
        """
        Approve token spending for specified address.

        Args:
            token (Contract): the contract address or instance of token to approve.
            spender (Address): the spender address, contract address or instance.
            amount (Optional[TokenAmount]): an amount to approve. (infinity)
            gas_price (Optional[GasPrice]): the gas price in TokenAmount. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)
            nonce (Optional[int]): a nonce of the sender address. (get it using the 'nonce' function)
            check_gas_price (bool): if True and the gas price is higher than that specified in the 'gas_price'
                argument, the 'GasPriceTooHigh' error will raise. (False)

        Returns:
            Tx: the instance of the sent transaction.

        """
        token_address, _ = await self.get_contract_attributes(contract=token)
        token_contract = await self.default_token(
            contract_address=token_address
        )
        spender = Web3.to_checksum_address(spender)

        if not amount:
            if is_approve_infinity:
                amount = CommonValues.InfinityInt
            else:
                amount = await self.get_balance(token_address=token_address)

        elif isinstance(amount, (int, float)):
            decimals = await self.get_decimals(contract_address=token_address)
            amount = TokenAmount(amount=amount, decimals=decimals).Wei

        else:
            amount = amount.Wei

        tx_params = {}

        if gas_price:
            tx_params = self.set_gas_price(
                gas_price=gas_price,
                tx_params=tx_params
            )

        if gas_limit:
            tx_params = self.set_gas_limit(
                gas_limit=gas_limit,
                tx_params=tx_params
            )

        data = token_contract.encodeABI('approve',
                                        args=TxArgs(
                                            spender=spender,
                                            amount=amount
                                        ).get_tuple())
        tx_params.update({
            'to': token_contract.address,
            'data': data,
            'nonce': nonce,
        })

        tx = await self.transaction.sign_and_send(tx_params=tx_params)
        return tx

    async def get(
        self,
        contract: ParamsTypes.Contract,
        abi: list | str | None = None
    ) -> AsyncContract | Contract:
        """
        Get a contract instance.

        Args:
            contract (ParamsTypes.Contract): the contract address or instance.
            abi (list | str | None, optional): the contract ABI. (get it using the 'get_abi' function)

        Returns:
            AsyncContract | Contract: the contract instance.
        """
        contract, contract_abi = await self.get_contract_attributes(contract)
        if not abi and not contract_abi:
            # todo: сделаем подгрузку abi из эксплорера (в том числе через proxy_address)
            raise ValueError("Can not get contract ABI")
        if not abi:
            abi = contract_abi

        if abi:
            return self.account_manager.w3.eth.contract(address=contract, abi=abi)

        return self.account_manager.w3.eth.contract(address=contract)

    async def get_approved_amount(
        self,
        token: ParamsTypes.Contract,
        spender: ParamsTypes.Contract,
        owner: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get approved amount of token.

        Args:
            token (Contract): the contract address or instance of token.
            spender (Contract): the spender address, contract address or instance.
            owner (Optional[Address]): the owner address. (imported to client address)

        Returns:
            TokenAmount: the approved amount.

        """
        contract_address, _ = await self.get_contract_attributes(contract=token)
        contract = await self.default_token(contract_address=contract_address)
        spender, _ = await self.get_contract_attributes(contract=spender)
        if not owner:
            owner = self.account_manager.account.address

        amount = await contract.functions.allowance(
            owner,
            spender,
        ).call()
        decimals = await self.get_decimals(contract_address=contract.address)

        return TokenAmount(amount, decimals, wei=True)

    async def get_balance(
        self,
        token_address: str | ChecksumAddress | None = None,
        address: str | ChecksumAddress | None = None,
        decimals: int = 18
    ) -> TokenAmount:
        """
        Get the balance of an Ethereum address.

        Parameters:
        - `token_address` (str | ChecksumAddress | None): The address of the token. If provided, retrieves the token balance.
        - `address` (str | ChecksumAddress | None): The Ethereum address for which to retrieve the balance.
        - `decimals` (int): The number of decimals for the token (default is 18).

        Returns:
        - `TokenAmount`: An object representing the token balance, including the amount and decimals.

        Note:
        - If `token_address` is provided, it retrieves the token balance using the specified token address.
        - If `token_address` is not provided, it retrieves the ETH balance using the Ethereum address.

        Example:
        ```python
        balance = await client.wallet.get_balance(token_address='0x123abc...', address='0x456def...')
        print(balance)
        # Output: TokenAmount(amount=123.45, decimals=18, wei=True)
        ```
        """
        if not address:
            address = self.account_manager.account.address

        address = Web3.to_checksum_address(address)

        if token_address:
            contract = await self.default_token(contract_address=token_address)

            amount = await contract.functions.balanceOf(address).call()
            decimals = await self.get_decimals(contract_address=contract.address)

        else:
            amount = await self.account_manager.w3.eth.get_balance(account=address)
            decimals = self.account_manager.network.decimals

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def get_decimals(self, contract_address: ParamsTypes.Address) -> int:
        """
        Get the number of decimals for a given token.

        Parameters:
        - `contract_address` (str | ChecksumAddress): The address of the token contract.

        Returns:
        - `int`: The number of decimals for the token.

        Example:
        ```python
        decimals = await client.wallet.get_decimals(contract_address='0x123abc...')
        print(decimals)
        # Output: 18
        """
        contract = await self.default_token(contract_address)
        decimals = await contract.functions.decimals().call()

        return decimals

    async def default_token(self, contract_address: ParamsTypes.Address) -> Contract | AsyncContract:
        """
        Get the default token contract instance for a given token address.

        Parameters:
        - `contract_address` (str | ChecksumAddress): The address of the token contract.

        Returns:
        - `Contract` | `AsyncContract`: The contract instance representing the token.

        Example:
        ```python
        token_contract = await client.wallet.default_token(contract_address='0x123abc...')
        print(token_contract)
        # Output: <Contract object at 0x...>
        """
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.account_manager.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract

    def set_gas_price(
        self,
        gas_price: ParamsTypes.GasPrice,
        tx_params: dict | TxParams
    ) -> dict | TxParams:
        """
        Set the gas price in the transaction parameters.

        Args:
            gas_price (ParamsTypes.GasPrice): The gas price to set.
            tx_params (dict | TxParams): The transaction parameters.

        Returns:
            dict | TxParams: The updated transaction parameters.

        """
        if isinstance(gas_price, float | int):
            gas_price = TokenAmount(
                amount=gas_price,
                decimals=self.account_manager.network.decimals,
                set_gwei=True
            )
        tx_params['gasPrice'] = gas_price.GWei
        return tx_params

    def set_gas_limit(
        self,
        gas_limit: ParamsTypes.GasLimit,
        tx_params: dict | TxParams,
    ) -> dict | TxParams:
        """
        Set the gas limit in the transaction parameters.

        Args:
            gas_limit (ParamsTypes.GasLimit): The gas limit to set.
            tx_params (dict | TxParams): The transaction parameters.

        Returns:
            dict | TxParams: The updated transaction parameters.

        """
        if isinstance(gas_limit, int):
            gas_limit = TokenAmount(
                amount=gas_limit,
                decimals=self.account_manager.network.decimals,
                wei=True
            )
        tx_params['gas'] = gas_limit.Wei
        return tx_params
