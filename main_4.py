import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.utils.helpers import sleep
from tasks.base_task import BaseTask
from tasks.layer_zero.coredao.coredao import CoreDaoBridge
from tasks.layer_zero.stargate.stargate import Stargate
from tasks.layer_zero.testnet_bridge.testnet_bridge import TestnetBridge
from tasks.woofi.woofi import WooFi
from tasks.zksync.mute.mute import Mute
from tasks.zksync.space_fi.space_fi import SpaceFi

from data.config import PRIVATE_KEYS


async def main():
    # client = Client(private_key=PRIVATE_KEYS[0], network=Networks.Polygon)

    # woofi = WooFi(client=client)
    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.USDC,
    #     to_token=TokenSymbol.MATIC,
    #     amount=1.1,
    #     multiplier_of_gas=1.2
    # )
    # print('Started Woofi')
    # res = await woofi.swap(swap_info)
    # print(res)

    # await asyncio.sleep(40)

    # client = Client(private_key=PRIVATE_KEYS[0], network=Networks.BSC)
    # stargate = Stargate(client=client)

    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.USDT,
    #     to_token=TokenSymbol.USDT,
    #     gas_price=2.5,
    #     to_network='polygon'
    # )
    # print('Started Stargate')
    # res = await stargate.swap(swap_info, max_fee=1.3)
    # print(res)

    # coredao = CoreDaoBridge(client=client)
    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.USDT,
    #     to_token=TokenSymbol.USDT,
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

    # client = Client(private_key=PRIVATE_KEYS[0], network=Networks.Zksync)
    # mute = Mute(client=client)

    # print('started Mute(ZkSync) 1')
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.ETH,
    #     to_token = TokenSymbol.USDC,
    #     min_percent=20,
    #     max_percent=50,
    #     slippage=1
    # )
    # res = await mute.swap(swap_info=swap_info)
    # print(res)
    # await sleep(5, 10)

    # print('started Mute(ZkSync) 2')
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.USDC,
    #     to_token = TokenSymbol.WBTC,
    #     slippage=1
    # )
    # res = await mute.swap(swap_info=swap_info)
    # print(res)
    # await sleep(5, 10)

    # print('started Mute(ZkSync) 3')
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.WBTC,
    #     to_token = TokenSymbol.ETH,
    #     slippage=0.95
    # )
    # res = await mute.swap(swap_info=swap_info)
    # print(res)
    # await sleep(5, 10)

    # print('started Mute(ZkSync) 4')
    # swap_info = SwapInfo(
    #     from_token = TokenSymbol.WBTC,
    #     to_token = TokenSymbol.ETH,
    #     slippage=1
    # )
    # res = await mute.swap(swap_info=swap_info)
    # print(res)
    # await sleep(5, 10)

    # space_fi = SpaceFi(client=client)

    # print('Started SpaceFi: ETH->USDC')
    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.ETH,
    #     to_token=TokenSymbol.USDC,
    #     amount=0.0006,
    #     slippage=1
    # )

    # res = await space_fi.swap(
    #     swap_info=swap_info
    # )

    # print(res)
    # await sleep(2, 10)

    # print('Started SpaceFi: USDT->ETH')
    # swap_info = SwapInfo(
    #     from_token=TokenSymbol.USDT,
    #     to_token=TokenSymbol.ETH,
    #     slippage=1
    # )

    # res = await space_fi.swap(
    #     swap_info=swap_info
    # )

    # print(res)

    # BaseTask.parse_params(
    #     params="0x7ff36ab500000000000000000000000000000000000000000000000000000000000002370000000000000000000000000000000000000000000000000000000000000080000000000000000000000000a4cb5d09a153073fcab95fd7e4afa5b95b9f65650000000000000000000000000000000000000000000000000000000065d6a33200000000000000000000000000000000000000000000000000000000000000020000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000bbeb516fb02a01611cbbe0453fe3c580d7281011"
    # )

    """
0x7ff36ab5
000000000000000000000000000000000000000000000000000000000017d8be - amountOut (USDC)
0000000000000000000000000000000000000000000000000000000000000080 - 128 (10)
000000000000000000000000e747990d5a3df6737851022cba3a32efe85684e7 - toAddress
0000000000000000000000000000000000000000000000000000000064ff27fd - deadline 
0000000000000000000000000000000000000000000000000000000000000002 - 2
0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91 - WETH
0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC

function_signature: 0x7ff36ab5
0000000000000000000000000000000000000000000000000000000000124de7 - amountOut (USDC)
0000000000000000000000000000000000000000000000000000000000000080 - 128 (10)
000000000000000000000000a4cb5d09a153073fcab95fd7e4afa5b95b9f6565 - toAddress
0000000000000000000000000000000000000000000000000000000065d540b2 - deadline 
0000000000000000000000000000000000000000000000000000000000000002 - 2
0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91 - WETH
0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC

function_signature: 0x7ff36ab5
0000000000000000000000000000000000000000000000000000000000124c1e - amountOut (USDC)
0000000000000000000000000000000000000000000000000000000065d53fe7 - deadline 
0000000000000000000000000000000000000000000000000000000000000080 - 128 (10)
000000000000000000000000a4cb5d09a153073fcab95fd7e4afa5b95b9f6565 - toAddress
0000000000000000000000000000000000000000000000000000000000000002 - 2
0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91 - WETH
0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC

function_signature: 0x7ff36ab5
000000000000000000000000000000000000000000000000000000000012455a - amountOut (USDC)
000000000000000000000000a4cb5d09a153073fcab95fd7e4afa5b95b9f6565 - toAddress
0000000000000000000000000000000000000000000000000000000065d53c7a - deadline 
0000000000000000000000000000000000000000000000000000000000000080
0000000000000000000000000000000000000000000000000000000000000002
0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91 - WETH
0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC
    """

if __name__ == '__main__':
    asyncio.run(main())
