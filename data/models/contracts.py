import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.dataclasses import DefaultAbis
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.contracts.native_contract_token import NativeTokenContract


class Contracts(Singleton):
    ''' 
    Arbitrum
    '''
    ARBITRUM_ETH = NativeTokenContract(title='ETH')

    ARBITRUM_ARB = RawContract(
        title='ARB',
        address='0x912CE59144191C1204E64559FE8253a0e49E6548',
        abi=DefaultAbis.Token
    )
    
    ARBITRUM_USDC = RawContract(
        title='USDC',
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        abi=DefaultAbis.Token
    )
    
    ARBITRUM_USDC_e = RawContract(
        title='USDC.e',
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        abi=DefaultAbis.Token
    )
    
    ARBITRUM_WBTC = RawContract(
        title='WBTC',
        address='0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        abi=DefaultAbis.Token
    )
    
    ''' 
    Polygon 
    '''
    POLYGON_MATIC = NativeTokenContract(title='MATIC')

    POLYGON_USDC = RawContract(
        title='USDC',
        address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
        abi=DefaultAbis.Token
    )
    
    POLYGON_USDC_e = RawContract(
        title='USDC.e',
        address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        abi=DefaultAbis.Token
    )

    POLYGON_WBTC = RawContract(
        title='WBTC',
        address='0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',
        abi=DefaultAbis.Token
    )
    
    """
    Avalanche
    """        
    AVALANCHE_USDC = RawContract(
        title='USDC',
        address='0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        abi=DefaultAbis.Token
    )

    @staticmethod
    def get_token(network: str, token_ticker: str) -> RawContract:
        contract_name = f'{network.upper()}_{token_ticker.upper()}'

        attr = getattr(Contracts, contract_name, None)

        if attr is None:
            raise exceptions.ContractNotExists(
                "The contract has not been added to Contracts")

        return attr
