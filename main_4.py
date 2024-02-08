import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from tasks.layer_zero import Stargate
from tasks.woofi.woofi import WooFi
from data.config import PRIVATE_KEYS


async def main():
    client = Client(private_key=PRIVATE_KEYS[0], network=Networks.BSC)

    woofi = WooFi(client=client)

    swap_info = SwapInfo(
        from_token=CurrencySymbol.BNB,
        to_token=CurrencySymbol.USDT,
        amount=0.0033,
        gas_price=1
    )
    print('Started Woofi')
    res = await woofi.swap(swap_info)
    print(res)

    await asyncio.sleep(40)

    stargate = Stargate(client=client)

    swap_info = SwapInfo(
        from_token=CurrencySymbol.USDT,
        to_token=CurrencySymbol.USDC_e,
        gas_price=2.5,
        to_network='polygon'
    )
    print('Started Stargate')
    res = await stargate.swap(swap_info, max_fee=0.8, dst_fee=1)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())
