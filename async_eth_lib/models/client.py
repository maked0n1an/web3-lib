from async_eth_lib.models.networks.network import Network
from async_eth_lib.models.networks.networks import Networks
from .account.account_manager import AccountManager
from .contracts.contract import Contract


class Client:
    def __init__(
        self,
        private_key: str | None = None,
        network: Network = Networks.Goerli,
        proxy: str | None = None,
        check_proxy: bool = True
    ) -> None:
        self.account_manager = AccountManager(
            private_key=private_key,
            network=network,
            proxy=proxy,
            check_proxy=check_proxy
        )

        self.contract = Contract(self.account_manager)