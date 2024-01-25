from web3 import Web3
from eth_typing import ChecksumAddress

from .token_amount import TokenAmount
from .account import Account
from .transactions import Transactions
from .contracts import Contracts
from .network import (
    Network,
    Networks
)


class Client:
    def __init__(
        self,
        private_key: str | None = None,
        network: Network = Networks.Goerli,
        proxy: str | None = None,
        check_proxy: bool = True
    ) -> None:
        self.account = Account(
            private_key=private_key,
            network=network,
            proxy=proxy,
            check_proxy=check_proxy
        )

        self.contracts = Contracts(self.account)
        self.transactions = Transactions(self.account)

    async def get_balance(
        self,
        token_address: str | ChecksumAddress | None = None,
        address: str | ChecksumAddress | None = None,
        decimals: int = 18
    ) -> TokenAmount:
        if not address:
            address = self.account.address

        address = Web3.to_checksum_address(address)

        if token_address:
            contract = await self.contracts.default_token(contract_address=token_address)

            amount = await contract.functions.balanceOf(address).call()
            decimals = await contract.functions.decimals().call()
        else:
            amount = await self.account.w3.eth.get_balance(account=address)

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )
