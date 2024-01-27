import asyncio

from async_eth_lib.models.client import Client
from async_eth_lib.models.networks.networks import Networks


with open('private_key.txt', 'r') as file:
    private_keys = [row.strip() for row in file]

async def main():
    client = Client(private_key=private_keys[0], network=Networks.Arbitrum)
    
    print(
        await client.transaction.get_gas_price()
    )
    print(
        await client.transaction.get_max_priority_fee()
    )
    
    

if __name__ == '__main__':
    asyncio.run(main())