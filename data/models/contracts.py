import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.dataclasses import DefaultAbis
from async_eth_lib.models.contracts.raw_contract import RawContract


class Contracts(Singleton):
    ARBITRUM_ETH = RawContract(
        title='ETH',
        address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        abi=DefaultAbis.Token,
        is_native_token=True
    )

    ARBITRUM_USDC = RawContract(
        title='USDC',
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        abi=DefaultAbis.Token
    )

    ARBITRUM_ARB = RawContract(
        title='ARB',
        address='0x912CE59144191C1204E64559FE8253a0e49E6548',
        abi=DefaultAbis.Token
    )

    POLYGON_MATIC = RawContract(
        title='MATIC',
        address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        abi=DefaultAbis.Token,
        is_native_token=True
    )

    POLYGON_USDC = RawContract(
        title='USDC',
        address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
        abi=DefaultAbis.Token
    )

    POLYGON_WBTC = RawContract(
        title='WBTC',
        address='0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',
        abi=DefaultAbis.Token
    )

    @staticmethod
    def get_token(network: str, token_ticker: str) -> RawContract:
        network = network.upper()
        contract_name = f'{network}_{token_ticker}'

        attr = getattr(Contracts, contract_name, None)

        if attr is None:
            raise exceptions.ContractNotExists(
                "The contract has not been added to Contracts")

        return attr
