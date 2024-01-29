import asyncio
from async_eth_lib.models.client import Client
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.utils.helpers import read_txt
from tasks.woofi import WooFi


async def main():
    pk: list = read_txt('private_key.txt')

    client = Client(private_key=pk[0], network=Networks.Arbitrum)
    woofi = WooFi(client=client)

    usdc_amount = TokenAmount(amount=0.0005)
    res = await woofi.swap_usdc_to_eth()
    print(res)
    
if __name__ == '__main__':
    asyncio.run(main())