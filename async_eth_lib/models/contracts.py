import json
from typing import Any
from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .account_manager import AccountManager
from .others.common import AutoRepr
from .others.params_types import ParamsTypes
from .others.dataclasses import DefaultAbis
from .others.token_amount import TokenAmount
from async_eth_lib.utils.helpers import (
    make_request,
    text_between
)


class Contracts:
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager

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
        if isinstance(contract, (AsyncContract, RawContract)):
            return contract.address, contract.abi

        return Web3.to_checksum_address(contract), None

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

    # async def get_approved_amount(
    #     self,
    #     token: types.Contract,

    # )

    async def default_token(self, contract_address: ChecksumAddress | str) -> Contract | AsyncContract:
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.account_manager.w3.eth.contract(
            address=contract_address, abi=DefaultAbis.Token)

        return contract


class RawContract(AutoRepr):
    """
    An instance of a raw contract.

    Attributes:
        title str: a contract title.
        address (ChecksumAddress): a contract address.
        abi list[dict[str, Any]] | str: an ABI of the contract.

    """
    title: str
    address: ChecksumAddress
    abi: list[dict[str, Any]]

    def __init__(
        self,
        title: str,
        address: str,
        abi: list[dict[str, Any]] | str
    ) -> None:
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi (Union[List[Dict[str, Any]], str]): an ABI of the contract.

        """
        self.title = title
        self.address = Web3.to_checksum_address(address)
        self.abi = json.loads(abi) if isinstance(abi, str) else abi
