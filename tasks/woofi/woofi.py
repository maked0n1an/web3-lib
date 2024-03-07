from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import ContractsFactory
from async_eth_lib.models.others.constants import LogStatus
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import sleep
from tasks._common.swap_task import SwapTask
from tasks.woofi.woofi_contracts import WoofiContracts


class WooFi(SwapTask):
    async def swap(
        self,
        swap_info: SwapInfo
    ) -> int:
        check_message = self.validate_swap_inputs(
            first_arg=swap_info.from_token,
            second_arg=swap_info.to_token,
            param_type='tokens'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        dex_contract = WoofiContracts.get_dex_contract(
            name='WooRouterV2',
            network=self.client.account_manager.network.name
        )

        contract = await self.client.contract.get(contract=dex_contract)
        swap_query = await self._create_swap_query(contract=contract, swap_info=swap_info)

        args = TxArgs(
            fromToken=swap_query.from_token.address,
            toToken=swap_query.to_token.address,
            fromAmount=swap_query.amount_from.Wei,
            minToAmount=swap_query.min_to_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple()),
        )
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            hexed_tx_hash = await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                swap_info=swap_info,
                tx_params=tx_params
            )

            if hexed_tx_hash:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f'{swap_query.from_token} {swap_query.amount_from}'
                )
                await sleep(15, 30)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        receipt_status, status, message = await self.perform_swap(
            swap_info, swap_query, tx_params
        )

        self.client.account_manager.custom_logger.log_message(
            status=status, message=message
        )

        return receipt_status

    async def _create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo
    ) -> SwapQuery:

        swap_query = await self.compute_source_token_amount(swap_info=swap_info)

        to_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )

        price_of_to_token = await contract.functions.tryQuerySwap(
            swap_query.from_token.address,
            to_token.address,
            swap_query.amount_from.Wei
        ).call()

        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            to_token_price=price_of_to_token,
            swap_info=swap_info
        )
