import time

from web3 import Web3
import web3.exceptions as web3_exceptions
from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContractFetcher, ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.swap_task import SwapTask


class SyncSwap(SwapTask):
    SYNC_SWAP_ROUTER = RawContract(
        title="SyncSwap Router",
        address="0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
        abi=read_json(
            path=("data", "abis", "zksync", "sync_swap", "abi.json")
        ),
    )

    LIQUIDITY_POOLS = {
        (TokenSymbol.ETH, TokenSymbol.USDC):
            "0x80115c708e12edd42e504c1cd52aea96c547c05c",
        (TokenSymbol.ETH, TokenSymbol.USDT):
            "0xd3D91634Cf4C04aD1B76cE2c06F7385A897F54D3",
        (TokenSymbol.ETH, TokenSymbol.BUSD):
            "0xad86486f1d225d624443e5df4b2301d03bbe70f6",
        (TokenSymbol.ETH, TokenSymbol.WBTC):
            "0xb3479139e07568ba954c8a14d5a8b3466e35533d",
    }

    async def swap(self, swap_info: SwapInfo) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=swap_info.from_token,
            second_arg=swap_info.to_token,
            param_type="tokens",
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        contract = await self.client.contract.get(contract=self.SYNC_SWAP_ROUTER)
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)
        from_token_is_eth = swap_info.from_token == TokenSymbol.ETH

        if from_token_is_eth:
            swap_query.from_token = ZkSyncTokenContracts.WETH

        if swap_info.to_token == TokenSymbol.ETH:
            swap_query.to_token = ZkSyncTokenContracts.WETH
        else: 
            swap_query.to_token = ZkSyncTokenContracts.get_token(
                token_symbol=swap_info.to_token
            )

        from_token_price = await self.get_binance_ticker_price(swap_info.from_token)
        second_token_price = await self.get_binance_ticker_price(swap_info.to_token)

        min_to_amount = float(swap_query.amount_from.Ether) * from_token_price \
            / second_token_price * (1 - swap_info.slippage / 100)

        swap_query.min_to_amount = TokenAmount(
            amount=min_to_amount,
            decimals=await self.client.contract.get_decimals(swap_query.to_token)
        )
        pool = self.LIQUIDITY_POOLS.get(
            (swap_info.to_token.upper(), swap_info.from_token.upper())
        ) or self.LIQUIDITY_POOLS.get(
            (swap_info.from_token.upper(), swap_info.to_token.upper())
        )
        if not pool:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=f"{swap_info.from_token} -> {swap_info.to_token}: not existed pool"
            )
            return False

        zfilled_from_token = self.to_cut_hex_prefix_and_zfill(
            swap_query.from_token.address
        )
        zfilled_address = self.to_cut_hex_prefix_and_zfill(
            self.client.account_manager.account.address
        )
        tokenIn = (
            TokenContractFetcher.ZERO_ADDRESS
            if from_token_is_eth
            else swap_query.from_token.address
        )

        params = TxArgs(
            path=[
                TxArgs(
                    steps=[
                        TxArgs(
                            pool=Web3.to_checksum_address(pool),
                            data=(
                                '0x' +
                                zfilled_from_token +
                                zfilled_address +
                                (
                                    "2"
                                    if from_token_is_eth
                                    else "1"
                                ).zfill(64)
                            ),
                            callback=TokenContractFetcher.ZERO_ADDRESS,
                            callbackData="0x",
                        ).get_tuple()
                    ],
                    tokenIn=tokenIn,
                    amountIn=swap_query.amount_from.Wei,
                ).get_tuple()
            ],
            amountOutMin=swap_query.min_to_amount.Wei,
            deadline=int(time.time() + 10 * 60),
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI("swap", args=params.get_tuple()),
            maxPriorityFeePerGas=0,
        )

        if swap_info.from_token != TokenSymbol.ETH:
            approved = await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                swap_info=swap_info,
                tx_params=tx_params,
            )
            if approved:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_query.from_token.title} {swap_query.amount_from.Ether}"
                )
                await sleep(8, 20)
            else:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.ERROR,
                    message=f"Can not approve"
                )
                return False
        else:
            tx_params["value"] = swap_query.amount_from.Wei
            
        try:
            receipt_status, status, message = await self.perform_swap(
                swap_info, swap_query, tx_params
            )            
            self.client.account_manager.custom_logger.log_message(
                status=status, message=message
            )
            
            return receipt_status
        except web3_exceptions.ContractCustomError as e:
            error = str(e)
            if '0xc9f52c71' in error:
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
