from async_eth_lib.models.networks.network import Network
from async_eth_lib.models.networks.networks import Networks
from .account.account_manager import AccountManager
from .contracts.contract import Contract


class Client:
    def __init__(
        self,
        account_id: int | None = None,
        private_key: str | None = None,
        network: Network = Networks.Goerli,
        proxy: str | None = None,
        check_proxy: bool = True,
        create_log_file_per_account: bool = False
    ) -> None:        
        self.account_manager = AccountManager(
            account_id=account_id,
            private_key=private_key,
            network=network,
            proxy=proxy,
            check_proxy=check_proxy,
            create_log_file_per_account=create_log_file_per_account
        )

        self.contract = Contract(self.account_manager)