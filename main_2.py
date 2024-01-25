import asyncio

from async_eth_lib import (
    Client,
    Networks
)

with open('private_key.txt', 'r') as file:
    private_keys = [row.strip() for row in file]

async def main():
    client = Client(private_key=private_keys[0], network=Networks.Arbitrum)
    
    print(
        await client.transactions.get_gas_price()
    )
    print(
        await client.transactions.get_max_priority_fee()
    )
    
    

if __name__ == '__main__':
    asyncio.run(main())