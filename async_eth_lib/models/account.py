import random
import requests

from web3 import Web3
from web3.eth import AsyncEth
from fake_useragent import UserAgent
from eth_typing import ChecksumAddress
from eth_account.signers.local import LocalAccount

from .network import Network, Networks
import async_eth_lib.utils.exceptions as exceptions


class Account:
    network: Network
    account: LocalAccount | None
    w3: Web3

    @property
    def address(self):
        return self.account.address

    def __init__(
        self,
        private_key: str | None = None,
        network: Network = Networks.Goerli,
        proxy: str | None = None,
        check_proxy: bool = True
    ) -> None:
        self.network = network
        self.proxy = proxy
        self._initialize_proxy(check_proxy)
        self._initialize_headers()
        self.w3 = Web3(
            Web3.AsyncHTTPProvider(
                endpoint_uri=self.network.rpc,
                request_kwargs={'proxy': self.proxy, 'headers': self.headers}
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )
        self._initialize_account(private_key)

    def _initialize_proxy(self, check_proxy: bool):
        if not self.proxy:
            return

        if 'http' not in self.proxy:
            self.proxy = f'http://{self.proxy}'

        if check_proxy:
            your_ip = requests.get(
                'http://eth0.me', proxies={'http': self.proxy, 'https': self.proxy}, timeout=10
            ).text.rstrip()

            if your_ip not in self.proxy:
                raise exceptions.InvalidProxy(
                    f"Proxy doesn't work! It's IP is {your_ip}")

    def _initialize_headers(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'User-Agent': UserAgent().random
        }

    def _initialize_account(self, private_key: str | None):
        if private_key:
            self.account = self.w3.eth.account.from_key(
                private_key=private_key)
        elif private_key == '':
            self.account = None
        else:
            self.account = self.w3.eth.account.create(
                extra_entropy=str(random.randint(1, 999_999_999)))

    async def get_nonce(self, address: str | ChecksumAddress | None = None) -> int:
        if not address:
            address = self.account.address
        nonce = await self.w3.eth.get_transaction_count(address)

        return nonce
