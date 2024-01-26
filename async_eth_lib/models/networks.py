import random
import requests

from typing import List
from web3 import Web3
from async_eth_lib.models.others.common import Singleton

import async_eth_lib.models.others.exceptions as exceptions


class Network:
    TxPath: str = "tx/"
    ContractPath: str = "contract/"
    AddressPath: str = "address/"

    def __init__(
        self,
        name: str,
        rpc: str | List[str],
        chain_id: int | None = None,
        tx_type: int = 0,
        coin_symbol: str | None = None,
        explorer: str | None = None
    ) -> None:
        self.name: str = name.lower()
        self.rpc: str = rpc if isinstance(rpc, str) else random.choice(rpc)
        self.chain_id: int | None = chain_id
        self.tx_type: int = tx_type
        self.coin_symbol: str | None = coin_symbol
        self.explorer: str | None = explorer

        self._initialize_chain_id()
        self._initialize_coin_symbol()
        self._coin_symbol_to_upper()

    def _initialize_chain_id(self):
        if self.chain_id:
            return
        try:
            self.chain_id = Web3(Web3.HTTPProvider(self.rpc)).eth.chain_id
        except Exception as err:
            raise exceptions.WrongChainId(f'Can not get chainId: {err}')

    def _initialize_coin_symbol(self):
        if self.coin_symbol:
            return
        try:
            response = requests.get(
                'https://chainid.network/chain.json').json()
            for network in response:
                if network['chainId'] == self.chain_id:
                    self.coin_symbol = network['nativeCurrency']['symbol']
                    break
        except Exception as err:
            raise exceptions.WrongCoinSymbol(
                f'Can not get coin symbol: {err}')

    def _coin_symbol_to_upper(self):
        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()


class Networks(Singleton):
    # Mainnet
    Ethereum = Network(
        name='ethereum',
        rpc='https://rpc.ankr.com/eth/720840b6beda865781b7beb539459137b7da7a657a58524b341d980a0a510f48',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://etherscan.io/',
    )

    Arbitrum = Network(
        name='arbitrum',
        rpc=[
            'https://rpc.ankr.com/arbitrum/720840b6beda865781b7beb539459137b7da7a657a58524b341d980a0a510f48',
            'https://rpc.ankr.com/arbitrum/a711c35e9e092e57fed201c2960689957eaf1ad37b7e7ec4eca11accd776e5a9'
        ],
        chain_id=42161,
        tx_type=2,
        coin_symbol='eth',
        explorer='https://arbiscan.io/'
    )

    ArbitrumNova = Network(
        name='arbitrum_nova',
        rpc='https://nova.arbitrum.io/rpc/',
        chain_id=42170,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://nova.arbiscan.io/',
    )

    Optimism = Network(
        name='optimism',
        rpc='https://rpc.ankr.com/optimism/',
        chain_id=10,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://optimistic.etherscan.io/',
    )

    BSC = Network(
        name='bsc',
        rpc='https://rpc.ankr.com/bsc/',
        chain_id=56,
        tx_type=0,
        coin_symbol='BNB',
        explorer='https://bscscan.com/',
    )

    Polygon = Network(
        name='polygon',
        rpc='https://rpc.ankr.com/polygon/',
        chain_id=137,
        tx_type=2,
        coin_symbol='MATIC',
        explorer='https://polygonscan.com/',
    )

    Avalanche = Network(
        name='avalanche',
        rpc='https://rpc.ankr.com/avalanche/',
        chain_id=43114,
        tx_type=2,
        coin_symbol='AVAX',
        explorer='https://snowtrace.io/',
    )

    Moonbeam = Network(
        name='moonbeam',
        rpc='https://rpc.api.moonbeam.network/',
        chain_id=1284,
        tx_type=2,
        coin_symbol='GLMR',
        explorer='https://moonscan.io/',
    )

    Fantom = Network(
        name='fantom',
        rpc='https://fantom.publicnode.com',
        chain_id=250,
        tx_type=0,
        coin_symbol='FTM',
        explorer='https://ftmscan.com/',
    )

    Celo = Network(
        name='celo',
        rpc='https://1rpc.io/celo',
        chain_id=42220,
        tx_type=0,
        coin_symbol='CELO',
        explorer='https://celoscan.io/',
    )

    Gnosis = Network(
        name='gnosis',
        rpc='https://rpc.ankr.com/gnosis',
        chain_id=100,
        tx_type=2,
        coin_symbol='xDAI',
        explorer='https://gnosisscan.io/',
    )

    HECO = Network(
        name='heco',
        rpc='https://http-mainnet.hecochain.com',
        chain_id=128,
        tx_type=2,
        coin_symbol='HECO',
        explorer='https://www.hecoinfo.com/en-us/',
    )

    # Testnets
    Goerli = Network(
        name='goerli',
        rpc='https://rpc.ankr.com/eth_goerli/',
        chain_id=5,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://goerli.etherscan.io/',
    )

    Sepolia = Network(
        name='sepolia',
        rpc='https://rpc.sepolia.org',
        chain_id=11155111,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://sepolia.etherscan.io',
    )
