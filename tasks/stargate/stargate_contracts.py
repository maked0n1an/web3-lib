from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.utils.helpers import read_json


class StargateContracts(Singleton):
    STARGATE_ABI = read_json(
        path=('data', 'abis', 'stargate', 'abi.json')
    )

    ARBITRUM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Arbitrum_USDC)',
        address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
        abi=STARGATE_ABI
    )

    ARBITRUM_ETH = RawContract(
        title='Stargate Finance: Router (Arbitrum_ETH)',
        address='0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
        abi=STARGATE_ABI
    )

    AVALANCHE_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Avalanche USDC)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ABI
    )

    AVALANCHE_USDT = RawContract(
        title='Stargate Finance: Router (Arbitrum USDT)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ABI
    )

    BSC_USDT = RawContract(
        title='Stargate Finance: Router (BSC USDT)',
        address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        abi=STARGATE_ABI
    )

    BSC_BUSD = RawContract(
        title='Stargate Finance: Router (BSC BUSD)',
        address='0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
        abi=STARGATE_ABI
    )

    FANTOM_USDC = RawContract(
        title='Stargate Finance: Router (Fantom USDC)',
        address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
        abi=STARGATE_ABI
    )

    POLYGON_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Polygon USDC)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ABI
    )
