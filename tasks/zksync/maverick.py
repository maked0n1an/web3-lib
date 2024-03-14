import time
from eth_typing import HexStr

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from async_eth_lib.models.contracts.contracts import TokenContractData, ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails
from async_eth_lib.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
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
        is_from_token_eth = swap_info.from_token == TokenSymbol.ETH
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

        tx_payload_details = MaverickData.get_tx_payload_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )
        encoded_path_payload = b''
        for address in tx_payload_details.swap_path:
            encoded_path_payload += Web3.to_bytes(hexstr=HexStr(address))

        account_address = self.client.account_manager.account.address
        contract = await self.client.contract.get(
            contract=self.MAVERICK_ROUTER
        )        
        if not is_from_token_eth:
            recipient_address = TokenContractData.ZERO_ADDRESS

            second_data = contract.encodeABI('unwrapWETH9', args=[
                swap_query.min_to_amount.Wei,
                self.client.account_manager.account.address,
            ])
        else:    
            recipient_address = account_address
                   
            second_data = contract.encodeABI('refundETH', args=[])      

        params = TxArgs(
            path=encoded_path_payload,
            recipient=recipient_address,
            deadline=int(time.time() + 10 * 60),
            amountIn=swap_query.amount_from.Wei,
            amountOutMinimum=swap_query.min_to_amount.Wei
        )
        
        swap_amount_data = contract.encodeABI(
            tx_payload_details.method_name,
            args=[params.get_list()]
        )            

        multicall_data = contract.encodeABI(
            'multicall',
            args=[
                [swap_amount_data, second_data]
            ]
        )

        tx_params = TxParams(
            to=contract.address,
            data=multicall_data,
            maxPriorityFeePerGas=0,
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
                await sleep(10, 20)
            else:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.ERROR,
                    message=f"Can not approve"
                )
                return False
        else:
            tx_params['value'] = swap_query.amount_from.Wei

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


class MaverickData(TxPayloadDetailsFetcher):
    LIQUIDITY_POOLS = {
        (TokenSymbol.ETH, TokenSymbol.USDC):
            "0x41c8cf74c27554a8972d3bf3d2bd4a14d8b604ab",            
        (TokenSymbol.USDC, TokenSymbol.BUSD):
            "0xe799043fb52ff46cc57ce8a8b1ac3f151ba270f7",
        (TokenSymbol.USDC, TokenSymbol.ETH):
            "0x57681331b6cb8df134dccb4b54dc30e8fcdf0ad8",
        (TokenSymbol.BUSD, TokenSymbol.ETH):
            "0x3ae63fb198652e294b8de4c2ef659d95d5ff28be"
    }

    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.ETH, TokenSymbol.USDC)],
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature="0xc04b8d59"
            ),
            TokenSymbol.BUSD: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.BUSD)],
                    ZkSyncTokenContracts.BUSD.address,
                ],
                function_signature="0xc04b8d59"
            ),
        },
        TokenSymbol.BUSD: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.BUSD.address,
                    LIQUIDITY_POOLS[(TokenSymbol.BUSD, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.WETH.address,
                ],
                function_signature='0xc04b8d59'
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.WETH.address,
                ],
                function_signature='0xc04b8d59'
            )
        }
    }
