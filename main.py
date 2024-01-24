import asyncio
from async_eth_lib import  (
    Client,
    Networks
)

async def check_wallet():
    while True:
        client = Client(network=Networks.Arbitrum)
        balance = await client.wallet.get_balance()
        print(f'{client.account.address} | {client.account.key.hex()} | {balance.Ether}')
        
        if balance.Wei != 0:
            with open('success-wallets.txt', 'a') as file:
                file.write(f'{client.account.address} | {client.account.key.hex()} | {balance.Ether}')
                

async def main(count):
    tasks = []
    for _ in range(count):
        tasks.append(asyncio.create_task(check_wallet()))
    await asyncio.gather(*tasks)


# async def main():
#     private_key = ""
#     client = Client(private_key=private_key, network=Networks.Arbitrum)
#     usdc = await client.contracts.default_token(contract_address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831')
#     print(type(usdc))
    
#     usdc_amount = await client.wallet.get_balance(token_address=usdc.address)
#     print(usdc_amount.Wei)
#     print(client.account.key)


if __name__ == '__main__':
    asyncio.run(main(10))
