import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.swap_task import SwapTask
from tasks.zksync.mute.mute_routes import MuteRoutes


class Mute(SwapTask):
    MUTE_UNIVERSAL = RawContract(
        title='Mute',
        address='0x8b791913eb07c32779a16750e3868aa8495f5964',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'mute', 'abi.json')
        )
    )

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
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

        contract = await self.client.contract.get(
            contract=self.MUTE_UNIVERSAL
        )

        swap_query = await self._create_swap_query(
            contract=contract,
            swap_info=swap_info
        )

        tx_payload_details = MuteRoutes.get_tx_payload_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )

        params = TxArgs(
            amountOutMin=swap_query.min_to_amount.Wei,
            path=tx_payload_details.swap_path,
            to=self.client.account_manager.account.address,
            deadline=int(time.time() + 20 * 60),
            stable=tx_payload_details.bool_list
        )

        list_params = params.get_list()

        if (
            swap_info.from_token != TokenSymbol.ETH
        ):
            list_params.insert(0, swap_query.amount_from.Wei)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                tx_payload_details.method_name,
                args=tuple(list_params)
            ),
            maxPriorityFeePerGas=0
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
                    message=f"{swap_query.from_token.title} {swap_query.amount_from.Ether}"
                )
                await sleep(8, 15)
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

        if swap_info.from_token == TokenSymbol.ETH:
            from_token = ZkSyncTokenContracts.WETH
        else:
            from_token = ZkSyncTokenContracts.get_token(
                swap_info.from_token
            )

        if swap_info.to_token == TokenSymbol.ETH:
            swap_query.to_token = ZkSyncTokenContracts.WETH
        else:
            swap_query.to_token = ZkSyncTokenContracts.get_token(
                swap_info.to_token
            )

        min_amount_out = await contract.functions.getAmountOut(
            swap_query.amount_from.Wei,
            from_token.address,
            swap_query.to_token.address
        ).call()

        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            to_token_price=min_amount_out[0],
            swap_info=swap_info
        )
