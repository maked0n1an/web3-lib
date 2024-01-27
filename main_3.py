import asyncio
import json
import aiohttp

from async_eth_lib.models.client import Client
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_txt
from data.models import Contracts

pk: list = read_txt('private_key.txt')

async def get_token_price(from_token, to_token) -> float | None:
    from_token, to_token = from_token.upper(), to_token.upper()

    async with aiohttp.ClientSession() as session:
        price = await get_price(session, f'{from_token}{to_token}')
        if price is None:
            price = await get_price(session, f'{to_token}{from_token}')

        return price


async def get_price(session: aiohttp.ClientSession, symbol) -> float | None:
    try:
        async with session.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}') as r:
            result_dict = await r.json()
            if 'price' in result_dict:
                return float(result_dict['price'])
    except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError):
        pass

    return None


async def get_min_to_amount(from_token: str, to_token: str, decimals: float = 0.5):
    token_price = await get_token_price(from_token=from_token, to_token=to_token)
    token_price = token_price * (1 - decimals / 100)

    return token_price

async def main():
    client = Client(private_key=pk[0], network=Networks.Arbitrum)
    
    from_token = Contracts.ARBITRUM_ETH
    to_token = Contracts.ARBITRUM_USDC
    
    woofi_contract = await client.contract.get(contract_address=Contracts.ARBITRUM_WOOFI)
    
    from_amount = TokenAmount(2)
    min_to_amount = TokenAmount(
        amount=float(from_amount.Ether) * await get_min_to_amount(from_token=from_token.title, to_token=to_token.title),
        # decimals=6
    )
    
    tx_args = TxArgs(
        fromToken=Contracts.ARBITRUM_USDC.address,
        toToken=Contracts.ARBITRUM_ETH.address,
        fromAmount=from_amount.Wei,
        minToAmount=min_to_amount.Wei,
        to=client.account_manager.account.address,
        rebateTo=client.account_manager.account.address
    )    
    data = woofi_contract.encodeABI('swap', args=tx_args.get_tuple())
    
    tx_params = {
        'to': Contracts.ARBITRUM_WOOFI.address,
        'data': data,
        'value': from_amount.Wei
    }
    
    tx = await client.contract.approve(
        token=Contracts.ARBITRUM_USDC.address,
        spender=Contracts.ARBITRUM_WOOFI.address,
        amount=2.5
    )
    
    tx = await client.contract.transaction.sign_and_send(tx_params=tx_params)
    receipt = await tx.wait_for_transaction_receipt(account_manager=client.account_manager, timeout=200)
    if receipt:
        print(f'Success: https://arbiscan.com/tx/{tx.hash.hex()}')
    else:
        print(f'Error: https://arbiscan.com/tx/{tx.hash.hex()}')
    
if __name__ == '__main__': 
    asyncio.run(main())