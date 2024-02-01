import asyncio

from web3.contract import Contract, AsyncContract
from web3.types import (
    TxParams
)
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from data.models.contracts import Contracts
from tasks.base_task import BaseTask


class WooFi(BaseTask):
    async def get_min_to_amount(
        self,
        contract: AsyncContract | Contract,
        swap_info: SwapInfo
    ) -> SwapQuery:
        from_token = Contracts.get_token(
            network=swap_info.network,
            token_ticker=swap_info.from_token
        )
        to_token = Contracts.get_token(
            network=swap_info.network,
            token_ticker=swap_info.to_token
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()

            if not swap_info.amount:
                amount_from = balance
            else:
                amount_from = TokenAmount(
                    amount=swap_info.amount
                )
        else:
            balance = await self.client.contract.get_balance(
                token_address=from_token.address
            )
            if not swap_info.amount:
                amount_from = balance
            else:
                amount_from = TokenAmount(
                    amount=swap_info.amount,
                    decimals=await self.client.contract.get_decimals(contract_address=from_token.address)
                )

        if amount_from.Wei > balance.Wei:
            amount_from = balance

        to_token_price = await contract.functions.tryQuerySwap(
            from_token.address,
            to_token.address,
            amount_from.Wei
        ).call()

        if to_token.is_native_token:
            min_to_amount = TokenAmount(
                amount=to_token_price * (1 - swap_info.slippage / 100),
                wei=True
            )
        else:
            min_to_amount = TokenAmount(
                amount=to_token_price * (1 - swap_info.slippage / 100),
                decimals=await self.client.contract.get_decimals(contract_address=to_token.address),
                wei=True
            )

        return SwapQuery(
            from_token=from_token,
            to_token=to_token,
            from_amount=amount_from,
            min_to_amount=min_to_amount
        )

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        if swap_info.from_token == swap_info.to_token:
            return 'Incorrect input for swap(): token1 == token2'
        
        swap_contract = self._get_network_swap_contract(
            network=self.client.account_manager.network.name
        )

        dex_contract = await self.client.contract.get(contract=swap_contract)
        swap_info.network = self.client.account_manager.network.name

        swap_query = await self.get_min_to_amount(contract=dex_contract, swap_info=swap_info)

        args = TxArgs(
            fromToken=swap_query.from_token.address,
            toToken=swap_query.to_token.address,
            fromAmount=swap_query.from_amount.Wei,
            minToAmount=swap_query.min_to_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=dex_contract.address,
            data=dex_contract.encodeABI('swap', args=args.get_tuple())
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_address=swap_query.from_token.address,
                spender=dex_contract.address,
                amount=swap_query.from_amount,
                is_approve_infinity=False
            )
            await asyncio.sleep(3)
        else:
            tx_params['value'] = swap_query.from_amount.Wei

        tx = await self.client.contract.transaction.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_tx_receipt(web3=self.client.account_manager.w3)

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath
            return (
                f'{swap_query.from_amount.Ether} {swap_query.from_token.title} was swapped to '
                f'{swap_query.min_to_amount.Ether} {swap_query.to_token.title} '
                f'via {swap_contract.title}: '
                f'{full_path + tx.hash.hex()}'
            )

        return (
            f'Failed swap {swap_query.from_amount.Ether} to {swap_query.to_token.title}'
            f'via {swap_contract.title}'
        )