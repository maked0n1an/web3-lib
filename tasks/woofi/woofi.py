import asyncio

from web3.types import TxParams
from async_eth_lib.models.others.params_types import ParamsTypes

from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.models.contracts.contracts import TokenContracts
from tasks.base_task import BaseTask
from tasks.woofi.woofi_contracts import WoofiContracts


class WooFi(BaseTask):
    async def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        """
        Get the minimum amount of tokens to receive after the swap.

        Args:
            contract (AsyncContract | Contract): The contract instance for the swap.
            swap_info (SwapInfo): Information about the swap.

        Returns:
            SwapQuery: The query for the swap.

        """
        check = self.validate_swap_inputs(
            first_arg=swap_info.from_token,
            second_arg=swap_info.to_token,
            arg_type='tokens'
        )
        if check:
            return check

        swap_contract = WoofiContracts.get_dex_contract(
            name='WooRouterV2',
            network=self.client.account_manager.network.name
        )

        dex_contract = await self.client.contract.get(contract=swap_contract)
        swap_query = await self.create_swap_query(contract=dex_contract, swap_info=swap_info)

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
        
        tx_params = self.set_gas_price_and_gas_limit(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=dex_contract.address,
                amount=swap_query.from_amount,
                gas_price=swap_info.gas_price,
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
            f'Failed swap {swap_query.from_amount.Ether} to {swap_query.to_token.title} '
            f'via {swap_contract.title}: '
            f'{full_path + tx.hash.hex()}'
        )

    async def create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo
    )-> SwapQuery:
        
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)
        
        price_of_to_token = await contract.functions.tryQuerySwap(
            swap_query.from_token.address,
            swap_query.to_token.address,
            swap_query.from_amount.Wei
        ).call()
        
        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            to_token_price=price_of_to_token,
            slippage=swap_info.slippage
        )