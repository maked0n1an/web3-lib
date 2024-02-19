import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.utils.helpers import sleep
from tasks.layer_zero.coredao.coredao import CoreDaoBridge
from tasks.layer_zero.testnet_bridge.testnet_bridge import TestnetBridge
from tasks.woofi.woofi import WooFi
from data.config import PRIVATE_KEYS
from tasks.zksync.mute.mute import Mute


async def main():
    client = Client(private_key=PRIVATE_KEYS[0], network=Networks.Arbitrum)

    # woofi = WooFi(client=client)
    # swap_info = SwapInfo(
    #     from_token=CurrencySymbol.BNB,
    #     to_token=CurrencySymbol.USDT,
    #     amount=0.0004,
    #     gas_price=1
    # )
    # print('Started Woofi')
    # res = await woofi.swap(swap_info)
    # print(res)

    # await asyncio.sleep(40)

    # stargate = Stargate(client=client)

    # swap_info = SwapInfo(
    #     from_token=CurrencySymbol.USDT,
    #     to_token=CurrencySymbol.USDC_E,
    #     gas_price=2.5,
    #     to_network='polygon'
    # )
    # print('Started Stargate')
    # res = await stargate.swap(swap_info, max_fee=3, dst_fee=0.4)
    # print(res)
    
    # coredao = CoreDaoBridge(client=client)
    # swap_info = SwapInfo(
    #     from_token=CurrencySymbol.USDT,
    #     to_token=CurrencySymbol.USDT,
    #     to_network='core',
    #     gas_price=1      
    # )
    # print('Started Coredao')
    # res = await coredao.bridge(swap_info=swap_info)
    # print(res)
    
    # testnet_bridge = TestnetBridge(client=client)
    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.GETH_LZ,
    #     to_token=TokenSymbol.GETH,
    #     to_network='goerli'   
    # )
    # print('Started TestnetBridge')
    # res = await testnet_bridge.bridge(swap_info=swap_info)
    # print(res)
    
    client = Client(private_key=PRIVATE_KEYS[0], network=Networks.Zksync)
    mute = Mute(client=client)
   
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.ETH,
    #     to_token = TokenSymbol.USDT,
    #     min_percent=10,
    #     max_percent=10,
    #     slippage=0.9
    # )
    
    # print('started Mute(ZkSync) 1')
    # res = await mute.swap(swap_info=swap_info)
    # print(res)
    # await sleep(5, 10)
    
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.USDT,
    #     to_token = TokenSymbol.USDC,
    #     min_percent=50,
    #     max_percent=100,
    #     slippage=0.9
    # )
    
    # print('started Mute(ZkSync) 2')
    # res = await mute.swap(swap_info=swap_info)
    # print(res)    
    # await sleep(5, 10)
    
    swap_info = SwapInfo(
        from_token = TokenSymbol.USDC,
        to_token = TokenSymbol.ETH,
        slippage=0.9
    )
    
    print('started Mute(ZkSync) 3')
    res = await mute.swap(swap_info=swap_info)
    print(res)
    await sleep(5, 10)

if __name__ == '__main__':
    asyncio.run(main())
