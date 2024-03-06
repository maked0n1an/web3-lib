import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.swap_task import SwapTask


class SyncSwap(SwapTask):
    SYNC_SWAP_ROUTER = RawContract(
        title='SyncSwap Router',
        address='0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'sync_swap', 'abi.json')
        )
    )

    USDC_WETH = RawContract(
        title='SyncSwap USDC/WETH Classic LP',
        address='0x80115c708e12edd42e504c1cd52aea96c547c05c',
        abi=None
    )

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> bool:
        contract = await self.client.contract.get(
            contract=self.SYNC_SWAP_ROUTER
        )
        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        to_token = ZkSyncTokenContracts.get_token(
            token_symbol=swap_info.to_token
        )
        from_token_price = await self.get_binance_ticker_price(
            first_token=swap_info.from_token
        )

        if swap_query.from_token.is_native_token:
            min_amount = float(swap_query.amount_from.Ether) * from_token_price \
                * (1 - swap_info.slippage / 100)

        else:
            second_token_price = await self.get_binance_ticker_price(
                first_token=swap_info.to_token
            )
            min_amount = float(swap_query.amount_from.Ether) * from_token_price \
                / second_token_price * (1 - swap_info.slippage / 100)

        swap_query.min_to_amount = TokenAmount(
            amount=min_amount, decimals=to_token.decimals
        )

        if swap_info.from_token == TokenSymbol.ETH:
            from_token_contract = ZkSyncTokenContracts.WETH
        else:
            from_token_contract = ZkSyncTokenContracts.get_token(
                token_symbol=swap_info.from_token
            )

        if swap_info.to_token == TokenSymbol.ETH:
            swap_query.to_token = ZkSyncTokenContracts.WETH
        else:
            swap_query.to_token = ZkSyncTokenContracts.get_token(
                token_symbol=swap_info.to_token
            )

        zfilled_pool_address = self.to_cut_hex_prefix_and_zfill(
            from_token_contract.address
        )
        zfilled_address = self.to_cut_hex_prefix_and_zfill(
            self.client.account_manager.account.address
        )

        params = TxArgs(
            path=[
                TxArgs(
                    steps=[
                        TxArgs(
                            pool=self.USDC_WETH.address,
                            data=(
                                f'0x'
                                f'{zfilled_pool_address}'
                                f'{zfilled_address}'
                                f'{"2".zfill(64)}'
                            ),
                            callback='0x0000000000000000000000000000000000000000',
                            callbackData='0x'
                        ).get_tuple()
                    ],
                    tokenIn='0x0000000000000000000000000000000000000000',
                    amountIn=swap_query.amount_from.Wei
                ).get_tuple()
            ],
            amountOutMin=swap_query.min_to_amount.Wei,
            deadline=int(time.time() + 10 * 60)
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=params.get_tuple()),
            maxPriorityFeePerGas=0
        )

        if not swap_query.from_token.is_native_token:
            result = await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params
            )
            if not result:
                await sleep(8, 20)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        receipt, status, message = await self.perform_swap(
            swap_info, swap_query, tx_params
        )

        self.client.account_manager.custom_logger.log_message(
            status=status, message=message
        )

        return receipt if receipt else False
