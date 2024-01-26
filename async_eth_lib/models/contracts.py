from web3 import Web3
from web3.contract import Contract, AsyncContract
from eth_typing import ChecksumAddress

from .account_manager import AccountManager
from .default_abis import DefaultAbis
from .token_amount import TokenAmount
from .types import types
from async_eth_lib.utils.helpers import make_request

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
