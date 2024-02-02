from async_eth_lib.models.others.constants import CurrencySymbol
import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.dataclasses import DefaultAbis
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.contracts.native_contract_token import NativeTokenContract


class Contracts(Singleton):
    ''' 
    Arbitrum
    '''
    ARBITRUM_ETH = NativeTokenContract(title=CurrencySymbol.ETH)

    ARBITRUM_ARB = RawContract(
        title=CurrencySymbol.ARB,
        address='0x912CE59144191C1204E64559FE8253a0e49E6548',
        abi=DefaultAbis.Token
    )

    ARBITRUM_USDC = RawContract(
        title=CurrencySymbol.USDC,
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        abi=DefaultAbis.Token
    )

    ARBITRUM_USDT = RawContract(
        title=CurrencySymbol.USDT,
        address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        abi=DefaultAbis.Token
    )

    ARBITRUM_DAI = RawContract(
        title=CurrencySymbol.DAI,
        address='0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        abi=DefaultAbis.Token
    )

    ARBITRUM_USDC_e = RawContract(
        title='USDC.e',
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        abi=DefaultAbis.Token
    )

    ARBITRUM_WBTC = RawContract(
        title=CurrencySymbol.WBTC,
        address='0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        abi=DefaultAbis.Token
    )

    """
    Avalanche
    """
    AVALANCHE_AVAX = NativeTokenContract(title=CurrencySymbol.AVAX)
    
    AVALANCHE_ETH = RawContract(
        title=CurrencySymbol.ETH,
        address='0xf20d962a6c8f70c731bd838a3a388d7d48fa6e15',
        abi=DefaultAbis.Token
    )
    
    AVALANCHE_USDC = RawContract(
        title=CurrencySymbol.USDC,
        address='0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        abi=DefaultAbis.Token
    )
    
    AVALANCHE_USDT = RawContract(
        title=CurrencySymbol.USDT,
        address='0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
        abi=DefaultAbis.Token
    )
    
    AVALANCHE_FRAX= RawContract(
        title=CurrencySymbol.FRAX,
        address='0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
        abi=DefaultAbis.Token
    )

    """
    BSC
    """
    BSC_BNB = NativeTokenContract(title=CurrencySymbol.BNB)

    BSC_USDT = RawContract(
        title=CurrencySymbol.USDT,
        address='0x55d398326f99059fF775485246999027B3197955',
        abi=DefaultAbis.Token
    )

    BSC_BUSD = RawContract(
        title=CurrencySymbol.BUSD,
        address='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
        abi=DefaultAbis.Token
    )
    
    """
    Fantom
    """
    FANTOM_USDC = RawContract(
        title=CurrencySymbol.USDC,
        address='0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf',
        abi=DefaultAbis.Token
    )

    """
    Optimism
    """
    OPTIMISM_USDC = RawContract(
        title=CurrencySymbol.USDC,
        address='0x7f5c764cbc14f9669b88837ca1490cca17c31607',
        abi=DefaultAbis.Token
    )
    
    OPTIMISM_DAI = RawContract(
        title=CurrencySymbol.DAI,
        address='0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        abi=DefaultAbis.Token
    )
    
    OPTIMISM_FRAX = RawContract(
        title=CurrencySymbol.FRAX,
        address='0x2E3D870790dC77A83DD1d18184Acc7439A53f475',
        abi=DefaultAbis.Token
    )

    """
    Polygon 
    """
    POLYGON_MATIC = NativeTokenContract(title=CurrencySymbol.MATIC)

    POLYGON_USDC = RawContract(
        title=CurrencySymbol.USDC,
        address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
        abi=DefaultAbis.Token
    )

    POLYGON_USDT = RawContract(
        title=CurrencySymbol.USDT,
        address='0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        abi=DefaultAbis.Token
    )

    POLYGON_DAI = RawContract(
        title=CurrencySymbol.DAI,
        address='0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
        abi=DefaultAbis.Token
    )

    POLYGON_USDC_e = RawContract(
        title=CurrencySymbol.USDC_e,
        address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        abi=DefaultAbis.Token
    )

    POLYGON_WBTC = RawContract(
        title=CurrencySymbol.WBTC,
        address='0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',
        abi=DefaultAbis.Token
    )

    @classmethod
    def get_token(cls, network: str, token_ticker: str) -> RawContract:
        contract_name = f'{network.upper()}_{token_ticker.upper()}'

        if not hasattr(cls, contract_name):
            raise exceptions.ContractNotExists(
                "The contract has not been added to Contracts")

        return getattr(cls, contract_name)
