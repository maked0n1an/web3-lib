import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.contracts.raw_contract import (
    TokenContract,
    NativeTokenContract
)
from async_eth_lib.utils.helpers import read_json


class TokenContracts(metaclass=Singleton):
    NATIVE_ETH = NativeTokenContract(title=TokenSymbol.ETH)

    ''' 
    Arbitrum
    '''
    ARBITRUM_ETH = NATIVE_ETH

    ARBITRUM_ARB = TokenContract(
        title=TokenSymbol.ARB,
        address='0x912CE59144191C1204E64559FE8253a0e49E6548',
        decimals=18
    )

    ARBITRUM_GETH = TokenContract(
        title=TokenSymbol.GETH,
        address='0xaF7355462240d5a8f3509BD890994AF1022F1948',
        decimals=18
    )

    ARBITRUM_GETH_LZ = TokenContract(
        title="GETH_LZ",
        address='0xdD69DB25F6D620A7baD3023c5d32761D353D3De9',
        decimals=18
    )

    ARBITRUM_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    )

    ARBITRUM_USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        decimals=6
    )

    ARBITRUM_DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        decimals=18
    )

    ARBITRUM_USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        decimals=6
    )

    ARBITRUM_WBTC = TokenContract(
        title=TokenSymbol.WBTC,
        address='0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
    )

    """
    Avalanche
    """
    AVALANCHE_AVAX = NativeTokenContract(title=TokenSymbol.AVAX)

    AVALANCHE_ETH = TokenContract(
        title=TokenSymbol.ETH,
        address='0xf20d962a6c8f70c731bd838a3a388d7d48fa6e15',
    )

    AVALANCHE_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        decimals=6
    )

    AVALANCHE_USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
    )

    AVALANCHE_FRAX = TokenContract(
        title=TokenSymbol.FRAX,
        address='0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
    )

    """
    BSC
    """
    BSC_BNB = NativeTokenContract(title=TokenSymbol.BNB)

    BSC_USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x55d398326f99059fF775485246999027B3197955',
    )

    BSC_BUSD = TokenContract(
        title=TokenSymbol.BUSD,
        address='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    )

    """
    Fantom
    """
    FANTOM_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
        decimals=6
    )

    FANTOM_USDC_E = TokenContract(
        title=TokenSymbol.USDC,
        address='0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf',
        decimals=6
    )

    """
    Optimism
    """
    OPTIMISM_ETH = NATIVE_ETH

    OPTIMISM_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        decimals=6
    )

    OPTIMISM_USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
        decimals=6
    )

    OPTIMISM_DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0xda10009cbd5d07dd0cecc66161fc93d7c9000da1'
    )

    OPTIMISM_FRAX = TokenContract(
        title=TokenSymbol.FRAX,
        address='0x2E3D870790dC77A83DD1d18184Acc7439A53f475'
    )

    """
    Polygon 
    """
    POLYGON_MATIC = NativeTokenContract(title=TokenSymbol.MATIC)

    POLYGON_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
        decimals=6
    )

    POLYGON_USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        decimals=6
    )

    POLYGON_USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        decimals=6
    )

    POLYGON_DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'
    )

    POLYGON_WBTC = TokenContract(
        title=TokenSymbol.WBTC,
        address='0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6'
    )

    """
    zkSync 
    """
    ZKSYNC_ETH = NATIVE_ETH
    
    ZKSYNC_WETH = TokenContract(
        title=TokenSymbol.WETH,
        address='0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'weth_abi.json')
        )
    )

    ZKSYNC_USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
    )

    @classmethod
    def get_token(
        cls,
        network: str,
        token_symbol: str,
        project_prefix: str | None = None,
    ) -> TokenContract:
        contract_name = (
            f'{network.upper()}_{token_symbol.upper()}_{project_prefix.upper()}'
            if project_prefix
            else f'{network.upper()}_{token_symbol.upper()}'
        )

        if not hasattr(cls, contract_name):
            raise exceptions.ContractNotExists(
                "The contract has not been added to Contracts")

        return getattr(cls, contract_name)
