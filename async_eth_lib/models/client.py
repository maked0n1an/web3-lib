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