from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .raw_contract import RawContract
from ..account.account_manager import AccountManager
from ..others.params_types import ParamsTypes
from ..others.dataclasses import CommonValues, DefaultAbis
from ..others.token_amount import TokenAmount
from ...models.transactions.transaction import Transaction
from ...models.transactions.tx import Tx
from ...models.transactions.tx_args import TxArgs
from ...utils.helpers import (
    make_request,
    text_between
)
import async_eth_lib.models.others.exceptions as exceptions


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
        # swap(address,address,uint256,uint256,address,address)

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

    async def get(
        self,
        contract_address: ParamsTypes.Contract,
        abi: list | str | None = None
    ) -> AsyncContract | Contract:
        """
        Get a contract instance.

        Args:
            contract_address (ParamsTypes.Contract): the contract address or instance.
            abi (list | str | None, optional): the contract ABI. (get it using the 'get_abi' function)

        Returns:
            AsyncContract | Contract: the contract instance.
        """
        contract_address, contract_abi = await self.get_contract_attributes(contract_address)
        if not abi and not contract_abi:
            # todo: сделаем подгрузку abi из эксплорера (в том числе через proxy_address)
            raise ValueError("Can not get contract ABI")
        if not abi:
            abi = contract_abi

        if abi:
            return self.account_manager.w3.eth.contract(address=contract_address, abi=abi)

        return self.account_manager.w3.eth.contract(address=contract_address)

    async def get_balance(
        self,
        token_address: str | ChecksumAddress | None = None,
        address: str | ChecksumAddress | None = None,
        decimals: int = 18
    ) -> TokenAmount:
        if not address:
            address = self.account_manager.account.address

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

    async def approve(
        self,
        token: ParamsTypes.Contract,
        spender: ParamsTypes.Address,
        amount: ParamsTypes.Amount | None = None,
        gas_price: ParamsTypes.GasPrice | None = None,
        gas_limit: ParamsTypes.GasLimit | None = None,
        nonce: int | None = None,
        check_gas_price: bool = False
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
        token_contract = await self.default_token(contract_address=token_address)
        spender = Web3.to_checksum_address(spender)

        if not amount:
            amount = CommonValues.InfinityInt

        elif isinstance(amount, (int, float)):
            decimals = await token_contract.functions.decimals().call()
            amount = TokenAmount(amount=amount, decimals=decimals).Wei

        else:
            amount = amount.Wei

        current_gas_price = await self.transaction.get_gas_price()
        tx_params = {}

        if gas_price:
            if check_gas_price and current_gas_price.Wei > gas_price.Wei:
                raise exceptions.GasPriceTooHigh()

            elif isinstance(gas_price, int):
                gas_price = TokenAmount(amount=gas_price, wei=True)
            tx_params['gasPrice'] = gas_price.Wei

        if gas_limit:
            if isinstance(gas_limit, int):
                gas_limit = TokenAmount(amount=gas_limit, wei=True)
            tx_params['gas'] = gas_limit.Wei

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
        spender, _ = await self.get_contract_attributes(spender=spender)
        if not owner:
            owner = self.account_manager.account.address

        amount = await contract.functions.allowance(
            owner,
            spender,
        ).call()
        decimals = await contract.functions.decimals().call()

        return TokenAmount(amount, decimals, wei=True)

    async def default_token(self, contract_address: ChecksumAddress | str) -> Contract | AsyncContract:
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.account_manager.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract
