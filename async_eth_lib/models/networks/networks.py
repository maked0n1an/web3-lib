import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.others.common import Singleton
from .network import Network


class Networks(Singleton):
    # Mainnet
    Ethereum = Network(
        name='ethereum',
        rpc='https://rpc.ankr.com/eth/720840b6beda865781b7beb539459137b7da7a657a58524b341d980a0a510f48',
        chain_id=1,
        tx_type=2,
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
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
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
        explorer='https://arbiscan.io/'
    )

    ArbitrumNova = Network(
        name='arbitrum_nova',
        rpc='https://nova.arbitrum.io/rpc/',
        chain_id=42170,
        tx_type=2,
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
        explorer='https://nova.arbiscan.io/',
    )

    Avalanche = Network(
        name='avalanche',
        rpc='https://rpc.ankr.com/avalanche/',
        chain_id=43114,
        tx_type=2,
        coin_symbol=CurrencySymbol.AVAX,
        decimals=18,
        explorer='https://snowtrace.io/',
    )

    BSC = Network(
        name='bsc',
        rpc='https://rpc.ankr.com/bsc/',
        chain_id=56,
        tx_type=0,
        coin_symbol=CurrencySymbol.BNB,
        decimals=18,
        explorer='https://bscscan.com/'
    )

    Celo = Network(
        name='celo',
        rpc='https://1rpc.io/celo',
        chain_id=42220,
        tx_type=0,
        coin_symbol=CurrencySymbol.CELO,
        decimals=18,
        explorer='https://celoscan.io/',
    )
    
    Core = Network(
        name='core',
        rpc='https://1rpc.io/core',
        chain_id=1116,
        tx_type=0,
        coin_symbol=CurrencySymbol.CORE,
        decimals=18,
        explorer='https://scan.coredao.org/',
    )

    Fantom = Network(
        name='fantom',
        rpc='https://fantom.publicnode.com',
        chain_id=250,
        tx_type=0,
        coin_symbol=CurrencySymbol.FTM,
        decimals=18,
        explorer='https://ftmscan.com/',
    )
    
    Gnosis = Network(
        name='gnosis',
        rpc='https://rpc.ankr.com/gnosis',
        chain_id=100,
        tx_type=2,
        coin_symbol=CurrencySymbol.XDAI,
        decimals=18,
        explorer='https://gnosisscan.io/',
    )

    Heco = Network(
        name='heco',
        rpc='https://http-mainnet.hecochain.com',
        chain_id=128,
        tx_type=2,
        coin_symbol=CurrencySymbol.HECO,
        decimals=18,
        explorer='https://www.hecoinfo.com/en-us/',
    )

    Moonbeam = Network(
        name='moonbeam',
        rpc='https://rpc.api.moonbeam.network/',
        chain_id=1284,
        tx_type=2,
        coin_symbol=CurrencySymbol.GLMR,
        decimals=18,
        explorer='https://moonscan.io/',
    )

    Optimism = Network(
        name='optimism',
        rpc='https://rpc.ankr.com/optimism/',
        chain_id=10,
        tx_type=2,
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
        explorer='https://optimistic.etherscan.io/',
    )
    
    Polygon = Network(
        name='polygon',
        rpc='https://rpc.ankr.com/polygon/',
        chain_id=137,
        tx_type=2,
        coin_symbol=CurrencySymbol.MATIC,
        decimals=18,
        explorer='https://polygonscan.com/',
    )

    # Testnets
    Goerli = Network(
        name='goerli',
        rpc='https://rpc.ankr.com/eth_goerli/',
        chain_id=5,
        tx_type=2,
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
        explorer='https://goerli.etherscan.io/',
    )

    Sepolia = Network(
        name='sepolia',
        rpc='https://rpc.sepolia.org',
        chain_id=11155111,
        tx_type=2,
        coin_symbol=CurrencySymbol.ETH,
        decimals=18,
        explorer='https://sepolia.etherscan.io',
    )
    
    @classmethod
    def get_network(
        cls, 
        network_name: str,
    ) -> Network:
        network_name = network_name.capitalize()

        if not hasattr(cls, network_name):
            raise exceptions.NetworkNotAdded(
                f"The network has not been added to {__class__.__name__} class"
            )

        return getattr(cls, network_name)