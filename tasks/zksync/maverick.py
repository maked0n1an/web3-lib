import time
from eth_typing import HexStr

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.path_details import PathDetails
from async_eth_lib.models.swap.path_details_fetcher import PathDetailsFetcher
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json
from tasks._common.swap_task import SwapTask


class Maverick(SwapTask):
    MAVERICK_ROUTER = RawContract(
        title="Maverick Router",
        address="0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4",
        abi=read_json(
            path=("data", "abis", "zksync", "maverick", "router_abi.json")
        ),
    )

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> bool:
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

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )
        swap_query.to_token = ZkSyncTokenContracts.get_token(
            swap_info.to_token
        )

        from_token_price = await self.get_binance_ticker_price(swap_info.from_token)
        second_token_price = await self.get_binance_ticker_price(swap_info.to_token)

        min_to_amount = float(swap_query.amount_from.Ether) * from_token_price \
            / second_token_price

        swap_query = await self.compute_min_destination_amount(
            swap_query=swap_query,
            to_token_price=min_to_amount,
            swap_info=swap_info
        )

        path_details = MaverickData.get_path_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )
        encoded_path_payload = b''
        for address in path_details.swap_path:
            encoded_path_payload += Web3.to_bytes(hexstr=HexStr(address))

        account_address = self.client.account_manager.account.address
        contract = await self.client.contract.get(
            contract=self.MAVERICK_ROUTER
        )

        params = TxArgs(
            path=encoded_path_payload,
            recipient=account_address,
            deadline=int(time.time() + 10 * 60),
            amountIn=swap_query.amount_from.Wei,
            amountOutMinimum=swap_query.min_to_amount.Wei
        )
        exact_input_data = contract.encodeABI(
            path_details.method_name,
            args=[params.get_list()]
        )
        refund_eth_method = contract.encodeABI('refundETH', args=[])

        multicall_data = contract.encodeABI(
            'multicall',
            args=[[exact_input_data, refund_eth_method]]
        )

        tx_params = TxParams(
            to=contract.address,
            data=multicall_data,
            maxPriorityFeePerGas=0,
        )

        try:
            receipt_status, log_status, message = await self.perform_swap(
                swap_info, swap_query, tx_params
            )

            self.client.account_manager.custom_logger.log_message(
                status=log_status, message=message
            )

            return receipt_status
        except web3_exceptions.ContractCustomError as e:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message='Try to make slippage more'
            )
        except Exception as e:
            error = str(e)
            if 'insufficient funds for gas + value' in error:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message='Insufficient funds for gas + value'
                )
            else:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=error
                )
        return False


class MaverickData(PathDetailsFetcher):
    LIQUIDITY_POOLS = {
        (TokenSymbol.ETH, TokenSymbol.USDC):
            "0x41c8cf74c27554a8972d3bf3d2bd4a14d8b604ab",
        (TokenSymbol.ETH, TokenSymbol.BUSD):
            "",
        (TokenSymbol.ETH, TokenSymbol.BUSD):
            "",
        (TokenSymbol.ETH, TokenSymbol.WBTC):
            "",
    }

    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: PathDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.ETH, TokenSymbol.USDC)],
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature="0xc04b8d59"
            ),
        }
    }
