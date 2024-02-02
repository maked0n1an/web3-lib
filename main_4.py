import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from data.config import PRIVATE_KEY
from tasks.woofi.woofi import WooFi


async def main():
    client = Client(private_key=PRIVATE_KEY, network=Networks.Polygon)
    woofi = WooFi(client=client)

    swap_info = SwapInfo(
        from_token='MATIC',
        to_token='WBTC',
        min_percent=40,
        max_percent=50,        
    )

    res = await woofi.swap(swap_info)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())
