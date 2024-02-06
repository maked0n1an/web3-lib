import asyncio
import json
import aiohttp

from async_eth_lib.models.client import Client
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_txt
from async_eth_lib.models.contracts.contracts import TokenContracts

pk: list = read_txt('private_key.txt')


async def get_token_price(from_token: str, to_token: str) -> float | None:
    from_token, to_token = from_token.upper(), to_token.upper()

    async with aiohttp.ClientSession() as session:
        price = await get_price(session, f'{from_token}{to_token}')
        if price is None:
            price = await get_price(session, f'{to_token}{from_token}')
            return 1 / price

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


async def get_min_to_amount(
    amount_to: TokenAmount,
    from_token: RawContract,
    to_token: RawContract,
    decimals: int,
    slippage: float = 0.5
) -> TokenAmount:
    to_token_price = await get_token_price(from_token=from_token.title, to_token=to_token.title)

    min_to_amount = TokenAmount(float(
        amount_to.Ether) * to_token_price * (1 - slippage / 100), decimals=decimals)

    return min_to_amount


async def main():
    client = Client(private_key=pk[0], network=Networks.Arbitrum)

    from_token = TokenContracts.ARBITRUM_USDC
    to_token = TokenContracts.ARBITRUM_ETH

    woofi_contract = await client.contract.get(contract=Dexes.WOOFI)

    amount_to = TokenAmount(
        2.26,
        decimals=6
    )
    min_to_amount = await get_min_to_amount(amount_to, from_token, to_token, 6)

    tx_args = TxArgs(
        fromToken=TokenContracts.ARBITRUM_USDC.address,
        toToken=TokenContracts.ARBITRUM_ETH.address,
        fromAmount=amount_to.Wei,
        minToAmount=min_to_amount.Wei,
        to=client.account_manager.account.address,
        rebateTo=client.account_manager.account.address
    )
    data = woofi_contract.encodeABI('swap', args=tx_args.get_tuple())

    tx_params = {
        'to': TokenContracts.ARBITRUM_WOOFI.address,
        'data': data,
        # 'value': amount_to.Wei
    }

    # tx = await client.contract.approve(
    #     token=Contracts.ARBITRUM_USDC.address,
    #     spender=Contracts.ARBITRUM_WOOFI.address,
    #     amount=amount_to
    # )
    # receipt = await tx.wait_for_transaction_receipt(account_manager=client.account_manager, timeout=200)
    # if receipt:
    #     print(f'Success: https://arbiscan.io/tx/{tx.hash.hex()}')
    # else:
    #     print(f'Error: https://arbiscan.io/tx/{tx.hash.hex()}')
    
    tx = await client.contract.transaction.sign_and_send(tx_params=tx_params)
    receipt = await tx.wait_for_tx_receipt(web3=client.account_manager.w3, timeout=200)
    if receipt:
        print(f'Success: https://arbiscan.io/tx/{tx.hash.hex()}')
    else:
        print(f'Error: https://arbiscan.io/tx/{tx.hash.hex()}')

if __name__ == '__main__':
    asyncio.run(main())
