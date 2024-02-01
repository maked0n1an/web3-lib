import asyncio
import aiohttp

from async_eth_lib.models.client import Client
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from data.models.dexes import Dexes


class BaseTask:
    def __init__(self, client: Client):
        self.client = client

    async def calculate_amount_from_for_swap(
        self,
        from_token: RawContract,
        swap_info: SwapInfo
    ) -> TokenAmount:
        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()

            if not swap_info.amount:
                token_amount = balance
            else:
                token_amount = TokenAmount(
                    amount=swap_info.amount
                )
        else:
            balance = await self.client.contract.get_balance(
                token_address=from_token.address
            )
            if not swap_info.amount:
                token_amount = balance
            else:
                token_amount = TokenAmount(
                    amount=swap_info.amount,
                    decimals=await self.client.contract.get_decimals(contract_address=from_token.address)
                )
                
        if swap_info.amount_by_percent:
            token_amount = TokenAmount(
                amount=balance.Wei * swap_info.amount_by_percent,
                decimals=token_amount.decimals,
                wei=True
            )

        if token_amount.Wei > balance.Wei:
            token_amount = balance

        return token_amount

    def get_network_swap_contract(self, network: str) -> RawContract:
        network = network.lower()
        dex = Dexes.get_dex(dex_name=self.__class__.__name__.upper())
        dex_contract = dex.contracts[network]

        return dex_contract

    async def get_binance_ticker_price(self, from_token: str, to_token: str) -> float | None:
        first_token, second_token = from_token.upper(), to_token.upper()
        async with aiohttp.ClientSession() as session:
            price = await self._get_price_from_binance(session, first_token, second_token)
            if price is None:
                price = await self._get_price_from_binance(session, second_token, first_token)
                return 1 / price

            return price

    async def approve_interface(
        self,
        token_address: str,
        spender: str,
        amount: TokenAmount | None = None,
        is_approve_infinity: bool = True
    ) -> bool:
        balance = await self.client.contract.get_balance(token_address=token_address)
        if balance.Wei <= 0:
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.contract.get_approved_amount(
            token=token_address,
            spender=spender,
            owner=self.client.account_manager.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        tx = await self.client.contract.approve(
            token=token_address,
            spender=spender,
            amount=amount,
            is_approve_infinity=is_approve_infinity
        )
        receipt = await tx.wait_for_tx_receipt(web3=self.client.account_manager.w3, timeout=300)
        if receipt:
            return True

        return False

    async def _get_price_from_binance(
        self,
        session: aiohttp.ClientSession,
        first_token: str = 'ETH',
        second_token: str = 'USDT'
    ) -> float | None:
        for _ in range(5):
            try:
                response = await session.get(
                    f'https://api.binance.com/api/v3/ticker/price?symbol={first_token}{second_token}')
                if response.status != 200:
                    return None
                result_dict = await response.json()
                if 'price' in result_dict:
                    return float(result_dict['price'])
            except Exception as e:
                await asyncio.sleep(3)
        raise ValueError(
            f'Can not get {first_token}{second_token} price from Binance')
