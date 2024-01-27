import asyncio
import json
from typing import Optional
import aiohttp
from hexbytes import HexBytes

from web3 import Web3
from web3.eth import AsyncEth
from eth_account.signers.local import LocalAccount
from async_eth_lib import (
    Client,
    Networks
)

contract_address = Web3.to_checksum_address(
    '0x9aed3a8896a85fe9a8cac52c9b402d092b629a30')
abi = json.loads(
    '[{"inputs":[{"internalType":"address","name":"_weth","type":"address"},{"internalType":"address","name":"_pool","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newPool","type":"address"}],"name":"WooPoolChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"enum IWooRouterV2.SwapType","name":"swapType","type":"uint8"},{"indexed":true,"internalType":"address","name":"fromToken","type":"address"},{"indexed":true,"internalType":"address","name":"toToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"fromAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"toAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"address","name":"rebateTo","type":"address"}],"name":"WooRouterSwap","type":"event"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"approveTarget","type":"address"},{"internalType":"address","name":"swapTarget","type":"address"},{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"internalType":"uint256","name":"minToAmount","type":"uint256"},{"internalType":"address payable","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"externalSwap","outputs":[{"internalType":"uint256","name":"realToAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"stuckToken","type":"address"}],"name":"inCaseTokenGotStuck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isWhitelisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"toAmount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"quoteToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newPool","type":"address"}],"name":"setPool","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"whitelisted","type":"bool"}],"name":"setWhitelisted","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"},{"internalType":"uint256","name":"minToAmount","type":"uint256"},{"internalType":"address payable","name":"to","type":"address"},{"internalType":"address","name":"rebateTo","type":"address"}],"name":"swap","outputs":[{"internalType":"uint256","name":"realToAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"fromToken","type":"address"},{"internalType":"address","name":"toToken","type":"address"},{"internalType":"uint256","name":"fromAmount","type":"uint256"}],"name":"tryQuerySwap","outputs":[{"internalType":"uint256","name":"toAmount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"wooPool","outputs":[{"internalType":"contract IWooPPV2","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]'
)


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


async def verif_tx(web3: Web3, tx_hash: HexBytes, timeout=180):
    try:
        data = await web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

        if data['status'] and data['status'] == 1:
            print(f"Successfull hash! - https://arbiscan.io/tx/{tx_hash.hex()}")
            return True
        
        else:
            print("Tx failed")
    except Exception as e:
        print(f"Some error occured: {e}")

    return False


async def main():
    web3 = Web3(
        provider=Web3.AsyncHTTPProvider(
            endpoint_uri=Networks.Arbitrum.rpc,
        ),
        modules={'eth': (AsyncEth,)},
        middlewares=[]
    )
    with open('private_key.txt', 'r') as file:
        mnemonics = [row.strip() for row in file]

    account: LocalAccount = web3.eth.account.from_key(private_key=mnemonics[0])
    wallet_address = account.address

    contract = web3.eth.contract(address=contract_address, abi=abi)

    from_token = Web3.to_checksum_address(
        '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    usdc_address = Web3.to_checksum_address(
        '0xaf88d065e77c8cC2239327C5EDb3A432268e5831')

    eth_amount = 0.00004
    min_usdc_amount = eth_amount * await get_min_to_amount(from_token='ETH', to_token='USDC')
    
    usdc_amount = 1.05
    min_eth_amount = usdc_amount / await get_min_to_amount(from_token='ETH', to_token='USDC')

    data = contract.encodeABI(
        'swap',
        args=(
            from_token,
            usdc_address,
            int(eth_amount * 10 ** 18),
            int(min_usdc_amount * 10 ** 6),
            wallet_address,
            wallet_address
        )
    )
    
    data2 = contract.encodeABI(
        'swap',
        args=(
            usdc_address,
            from_token,
            int(min_eth_amount * 10 ** 6),
            int(eth_amount * 10 ** 18),
            wallet_address,
            wallet_address
        )
    )

    tx_data = {
        'chainId': await web3.eth.chain_id,
        'gasPrice': await web3.eth.gas_price,
        'nonce': await web3.eth.get_transaction_count(wallet_address),
        'from': web3.to_checksum_address(wallet_address),
        'to': web3.to_checksum_address(contract_address),
        'data': data2,
        'value': int(eth_amount * 10 ** 18)
    }

    tx_data['gas'] = await web3.eth.estimate_gas(tx_data)

    sign = web3.eth.account.sign_transaction(tx_data, account.key)
    tx_hash: HexBytes = await web3.eth.send_raw_transaction(sign.rawTransaction)

    result = await verif_tx(web3, tx_hash=tx_hash)

    print(result)


if __name__ == '__main__':
    asyncio.run(main())
