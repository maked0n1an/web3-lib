from web3.types import TxParams
from async_eth_lib.models.others.constants import LogStatus

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
        check = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check:
            return check

        token_bridge_info = TestnetBridgeData.get_token_bridge_info(
            network=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )
        contract = await self.client.contract.get(
            contract=token_bridge_info.bridge_contract
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
            _zroPaymentAddress='0x0000000000000000000000000000000000000000',
            _adapterParams='0x'
        )

        value = await self._get_estimateSendFee(
            contract=contract,
            to_token=swap_info.to_token,
            swap_query=swap_query
        )

        tx_params = TxParams(
            to=token_bridge_info.bridge_contract.address,
            data=contract.encodeABI('sendFrom', args=args.get_tuple()),
            value=value.Wei
        )
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=token_bridge_info.bridge_contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params,
                is_approve_infinity=False
            )
            await sleep(10, 30)
        else:
            return f'Failed: can not approve'

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3,
            timeout=250
        )

        account_network = self.client.account_manager.network
        full_path = account_network.explorer + account_network.TxPath
        rounded_amount = round(swap_query.amount_from.Ether, 5)

        if receipt:
            status = LogStatus.BRIDGED
            message = (
                f'{rounded_amount} {swap_info.from_token} '
                f'was sent from {account_network.name.upper()} '
                f'to {swap_info.to_network.upper()}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()} '
            )
        else:
            status = LogStatus.ERROR
            message = (
                f'Failed cross-chain swap {rounded_amount} to {swap_query.to_token.title}: '
                f'{full_path + tx.hash.hex()}'
            )

        self.client.account_manager.custom_logger.log_message(
            status=status, message=message
        )

        return receipt if receipt else False

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
