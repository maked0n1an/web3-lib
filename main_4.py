import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from tasks.stargate.stargate import Stargate
from tasks.woofi.woofi import WooFi
from data.config import PRIVATE_KEY


async def main():
    client = Client(private_key=PRIVATE_KEY, network=Networks.Polygon)
    woofi = WooFi(client=client)
    stargate = Stargate(client=client)

    swap_info = SwapInfo(
        from_token=CurrencySymbol.USDC,
        to_token=CurrencySymbol.USDC_e,
        amount=0.0034,
        gas_price=1
    )
    print('Started Woofi')
    res = await woofi.swap(swap_info)
    print(res)
    
    swap_info = SwapInfo(
        from_token=CurrencySymbol.USDC_e,
        to_token=CurrencySymbol.USDT,
        to_network='bsc'
    )
    print('Started Stargate')
    res = await stargate.swap(swap_info)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())
