from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContractFetcher
from async_eth_lib.models.others.constants import (
    LogStatus
)

from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import sleep
from tasks._common.swap_task import SwapTask
from tasks.layer_zero.testnet_bridge.testnet_bridge_data import TestnetBridgeData


class TestnetBridge(SwapTask):
    chain_ids = {
        'GETH': 154
    }

    async def bridge(
        self,
        swap_info: SwapInfo
    ) -> str:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        src_bridge_data = TestnetBridgeData.get_token_bridge_info(
            network=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )
        contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        args = TxArgs(
            _from=self.client.account_manager.account.address,
            _dstChainId=TestnetBridge.chain_ids[swap_info.to_token],
            _toAddress=self.client.account_manager.account.address,
            _amount=swap_query.amount_from.Wei,
            _refundAddress=self.client.account_manager.account.address,
            _zroPaymentAddress=TokenContractFetcher.ZERO_ADDRESS,
            _adapterParams='0x'
        )

        value = await self._get_estimateSendFee(
            contract=contract,
            to_token=swap_info.to_token,
            swap_query=swap_query
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('sendFrom', args=args.get_tuple()),
            value=value.Wei
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
                await sleep(20, 50)
        else:
            tx_params['value'] += swap_query.amount_from.Wei        

        receipt_status, log_status, log_message = await self.perform_bridge(
            swap_info, swap_query, tx_params, 
            external_explorer='https://layerzeroscan.com'
        ) 

        self.client.account_manager.custom_logger.log_message(
            status=log_status, message=log_message
        )

        return receipt_status

    async def _get_estimateSendFee(
        self,
        contract: ParamsTypes.Contract,
        to_token: str,
        swap_query: SwapQuery,
    ) -> TokenAmount:
        address = self.client.account_manager.account.address

        result = await contract.functions.estimateSendFee(
            TestnetBridge.chain_ids[to_token],
            address,
            swap_query.amount_from.Wei,
            False,
            '0x'
        ).call()

        return TokenAmount(amount=result[0], wei=True)
