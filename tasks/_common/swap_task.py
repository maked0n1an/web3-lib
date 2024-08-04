import asyncio
import aiohttp

from eth_typing import HexStr
from web3.types import (
    TxParams,
    TxReceipt,
    _Hash32,
)

from async_eth_lib.models.client import Client
from async_eth_lib.models.contracts.contracts import ContractsFactory
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery


class SwapTask:
    def __init__(self, client: Client):
        self.client = client

    @staticmethod
    def parse_params(
        params: str,
        has_function: bool = True
    ) -> None:
        if has_function:
            function_signature = params[:10]
            print('function_signature:', function_signature)
            params = params[10:]

        count = 0
        while params:
            memory_address = hex(count * 32)[2:].zfill(3)
            print(f'{memory_address}: {params[:64]}')
            count += 1
            params = params[64:]

    def to_cut_hex_prefix_and_zfill(self, data: str | HexStr, length: int = 64):
        """
        Convert the string to lowercase and fill it with zeros to the specified length.

        Args:
            length (int): The desired length of the string after filling.

        Returns:
            str: The modified string.
        """
        return data[2:].zfill(length)

    def set_all_gas_params(
        self,
        swap_info: SwapInfo,
        tx_params: dict | TxParams
    ) -> dict | TxParams:
        if swap_info.gas_limit:
            tx_params = self.client.contract.set_gas_limit(
                gas_limit=swap_info.gas_limit,
                tx_params=tx_params
            )

        if swap_info.gas_price:
            tx_params = self.client.contract.set_gas_price(
                gas_price=swap_info.gas_price,
                tx_params=tx_params
            )

        if swap_info.multiplier_of_gas:
            tx_params = self.client.contract.add_multiplier_of_gas(
                multiplier=swap_info.multiplier_of_gas,
                tx_params=tx_params
            )

        return tx_params

    def validate_swap_inputs(
        self,
        first_arg: str,
        second_arg: str,
        param_type: str = 'args'
    ) -> str:
        if first_arg.upper() == second_arg.upper():
            return f'The {param_type} for swap() are equal: {first_arg} == {second_arg}'

    async def approve_interface(
        self,
        token_contract: ParamsTypes.TokenContract,
        spender_address: ParamsTypes.Address,
        swap_info: SwapInfo,
        amount: ParamsTypes.Amount | None = None,
        tx_params: TxParams | dict | None = None,
        is_approve_infinity: bool = None
    ) -> bool:
        """
        Approve spending of a specific amount by a spender on behalf of the owner.

        Args:
            token_contract (ParamsTypes.TokenContract): The token contract instance.
            spender_address (ParamsTypes.Address): The address of the spender.
            amount (TokenAmount | None): The amount to approve (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).
            is_approve_infinity (bool): Whether to approve an infinite amount (default is True).

        Returns:
            bool: True if the approval is successful, False otherwise.

        Example:
        ```python
        approved = await approve_interface(
            token_contract=my_token_contract,
            spender_address='0x123abc...',
            amount=TokenAmount(amount=100, decimals=18),
            gas_price=20,
            gas_limit=50000,
            is_approve_infinity=False
        )
        print(approved)
        # Output: True
        ```
        """
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        balance = await self.client.contract.get_balance(
            token_contract=token_contract
        )
        if balance.Wei <= 0:
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.contract.get_approved_amount(
            token_contract=token_contract,
            spender_address=spender_address,
            owner=self.client.account_manager.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        hexed_tx_hash = await self.client.contract.approve(
            token_contract=token_contract,
            spender_address=spender_address,
            amount=amount,
            tx_params=tx_params,
            is_approve_infinity=is_approve_infinity
        )

        return bool(hexed_tx_hash)

    async def compute_source_token_amount(
        self,
        swap_info: SwapInfo
    ) -> SwapQuery:
        """
        Compute the source token amount for a given swap.

        Args:
            swap_info (SwapInfo): Information about the swap.

        Returns:
            SwapQuery: The query for the swap.

        Example:
        ```python
        swap_query = await compute_source_token_amount(swap_info=my_swap_info)
        print(swap_query)
        # Output: SwapQuery(from_token=..., to_token=..., amount_to=...)
        ```
        """
        from_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()

            if not swap_info.amount:
                token_amount = balance
            else:
                token_amount = TokenAmount(
                    amount=swap_info.amount,
                    decimals=self.client.account_manager.network.decimals
                )
        else:
            balance = await self.client.contract.get_balance(
                token_contract=from_token
            )
            if not swap_info.amount:
                token_amount = balance
            else:
                decimals = (
                    from_token.decimals
                    if from_token.decimals
                    else await self.client.contract.get_decimals(token_contract=from_token)
                )

                token_amount = TokenAmount(
                    amount=swap_info.amount,
                    decimals=decimals
                )

        if swap_info.amount_by_percent:
            token_amount = TokenAmount(
                amount=balance.Wei * swap_info.amount_by_percent,
                decimals=token_amount.decimals,
                wei=True
            )

        if token_amount.Wei > balance.Wei:
            token_amount = balance

        return SwapQuery(
            from_token=from_token,
            amount_from=token_amount
        )

    async def compute_min_destination_amount(
        self,
        swap_query: SwapQuery,
        to_token_price: float,
        swap_info: SwapInfo,
        is_to_token_price_wei: bool = False
    ) -> SwapQuery:
        """
        Compute the minimum destination amount for a given swap.

        Args:
            swap_query (SwapQuery): The query for the swap.
            to_token_price (float): The price of the destination token.
            slippage (int): The slippage tolerance.

        Returns:
            SwapQuery: The updated query with the minimum destination amount.

        Example:
        ```python
        min_destination_query = await compute_min_destination_amount(
            swap_query=my_swap_query,
            to_token_price=my_token_price,
            slippage=1
        )
        print(min_destination_query)
        # Output: SwapQuery(from_token=..., to_token=..., amount_to=..., min_to_amount=...)
        ```
        """

        if not swap_query.to_token:
            swap_query.to_token = ContractsFactory.get_contract(
                network_name=self.client.account_manager.network.name,
                token_symbol=swap_info.to_token
            )

        decimals = 0
        if swap_query.to_token.is_native_token:
            decimals = self.client.account_manager.network.decimals

        else:
            decimals = await self.client.contract.get_decimals(
                token_contract=swap_query.to_token
            )

        min_to_amount = TokenAmount(
            amount=to_token_price * (1 - swap_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return SwapQuery(
            from_token=swap_query.from_token,
            amount_from=swap_query.amount_from,
            to_token=swap_query.to_token,
            min_to_amount=min_to_amount
        )

    async def perform_bridge(
        self,
        swap_info: SwapInfo,
        swap_query: SwapQuery,
        tx_params: TxParams | dict,
        external_explorer: str = None
    ) -> tuple[int, str, str]:
        """
        Perform a bridge operation.

        Args:
            swap_info (SwapInfo): Information about the swap.
            swap_query (SwapQuery): Query parameters for the swap.
            tx_params (TxParams | dict): Transaction parameters.
            external_explorer (str, optional): External explorer URL. Defaults to None.

        Returns:
            tuple[str, str]: A tuple containing:
                - A boolean indicating whether the bridge operation was successful.
                - Status of the bridge operation.
                - Message regarding the bridge operation.
        """
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx_hash, receipt = await self._perform_tx(tx_params)

        account_network = self.client.account_manager.network

        if external_explorer:
            full_path = external_explorer + account_network.TxPath
        else:
            full_path = account_network.explorer + account_network.TxPath

        rounded_amount = round(swap_query.amount_from.Ether, 5)

        if receipt['status']:
            status = LogStatus.BRIDGED
            message = f'{rounded_amount} {swap_info.from_token}'
        else:
            status = LogStatus.ERROR
            message = f'Failed bridge {rounded_amount} {swap_info.from_token}'

        message += (
            f' from {account_network.name.upper()} -> '
            f'{swap_info.to_network.upper()}: '
            f'{full_path + tx_hash.hex()}'
        )

        return receipt['status'], status, message

    async def perform_swap(
        self,
        swap_info: SwapInfo,
        swap_query: SwapQuery,
        tx_params: TxParams | dict,
    ) -> tuple[int, str, str]:
        """
        Perform a token swap operation.

        Args:
            swap_info (SwapInfo): Information about the swap.
            swap_query (SwapQuery): Query parameters for the swap.
            tx_params (TxParams | dict): Transaction parameters.

        Returns:
            tuple[bool, str, str]: A tuple containing:
                - A boolean indicating whether the swap was successful.
                - Status of the swap.
                - Message regarding the swap.
        """
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx_hash, receipt = await self._perform_tx(tx_params)

        account_network = self.client.account_manager.network
        full_path = account_network.explorer + account_network.TxPath
        rounded_amount = round(swap_query.amount_from.Ether, 5)

        if receipt['status']:
            log_status = LogStatus.SWAPPED
            message = f'{rounded_amount} {swap_info.from_token}'

        else:
            log_status = LogStatus.ERROR
            message = f'Failed swap {rounded_amount} {swap_info.from_token}'

        message += (
            f' -> {swap_query.min_to_amount.Ether} {swap_info.to_token}: '
            f'{full_path + tx_hash.hex()}'
        )

        return receipt['status'], log_status, message

    async def get_binance_ticker_price(
        self,
        first_token: str = TokenSymbol.ETH,
        second_token: str = TokenSymbol.USDT
    ) -> float | None:
        stable_coins = [
            TokenSymbol.USDT,
            TokenSymbol.USDC,
            TokenSymbol.USDC_E,
            TokenSymbol.BUSD
        ]
        
        if first_token.startswith('W'):
            first_token = first_token[1:]

        if second_token.startswith('W'):
            second_token = second_token[1:]

        if first_token in stable_coins:
            return 1

        async with aiohttp.ClientSession() as session:
            price = await self._get_price_from_binance(session, first_token, second_token)
            if price is None:
                price = await self._get_price_from_binance(session, first_token, second_token)
                return 1 / price

            return price

    async def get_token_info(self, token_address):
        contract = await self.client.contract.get_token_contract(token=token_address)
        print('=' * 50)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    async def _perform_tx(
        self,
        tx_params: TxParams | dict
    ) -> tuple[_Hash32, TxReceipt]:
        """
        Perform a token swap operation.

        Args:
            swap_info (SwapInfo): Information about the swap.
            tx_params (TxParams | dict): Transaction parameters.

        Returns:
            tuple[_Hash32, TxReceipt].
            - A tuple containing:
                - The hash of the transaction.
                - The receipt of the transaction.
        """
        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        return tx.hash, receipt

    async def _get_price_from_binance(
        self,
        session: aiohttp.ClientSession,
        first_token: str,
        second_token: str
    ) -> float | None:
        first_token, second_token = first_token.upper(), second_token.upper()
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
