import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.utils.helpers import read_txt
from tasks.woofi import WooFi


async def main():
    pk: list = read_txt('private_key.txt')

    client = Client(private_key=pk[0], network=Networks.Polygon)
    woofi = WooFi(client=client)

    swap_info = SwapInfo(
        'USDC',
        'MATIC',
        amount=1.5
    )

    res = await woofi.swap(swap_info)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())
