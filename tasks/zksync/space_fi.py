import time

from web3.types import TxParams
import web3.exceptions as web3_exceptions

from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import LogStatus, TokenSymbol
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.path_details import PathDetails
from async_eth_lib.models.swap.path_details_fetcher import PathDetailsFetcher
from async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.swap_task import SwapTask


class SpaceFi(SwapTask):
    SPACE_FI_ROUTER = RawContract(
        title='SpaceFiRouter',
        address='0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'space_fi', 'abi.json')
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

        account_address = self.client.account_manager.account.address
        contract = await self.client.contract.get(
            contract=self.SPACE_FI_ROUTER
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        swap_query.to_token = ZkSyncTokenContracts.get_token(
            token_symbol=swap_info.to_token
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

        tx_payload_details = SpaceFiRoutes.get_path_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )

        if swap_info.from_token != TokenSymbol.ETH:
            memory_address = 128 + 32
        else:
            memory_address = 128

        data = [
            f'{tx_payload_details.function_signature}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(swap_query.min_to_amount.Wei))}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(memory_address))}',
            f'{self.to_cut_hex_prefix_and_zfill(account_address).lower()}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(int(time.time() + 20 * 60)))}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(len(tx_payload_details.swap_path)))}'
        ]

        for contract_address in tx_payload_details.swap_path:
            data.append(
                self.to_cut_hex_prefix_and_zfill(contract_address.lower())
            )

        if swap_info.from_token != TokenSymbol.ETH:
            data.insert(1, self.to_cut_hex_prefix_and_zfill(
                hex(swap_query.amount_from.Wei)))

        data = ''.join(data)

        tx_params = TxParams(
            to=contract.address,
            data=data,
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
                await sleep(8, 20)
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


class SpaceFiRoutes(PathDetailsFetcher):
    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: PathDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.USDT: PathDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDT.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.WBTC: PathDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                function_signature="0x7ff36ab5"
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: PathDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.SPACE.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.WBTC: PathDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                function_signature='0x38ed1739'
            )
        },
        TokenSymbol.USDT: {
            TokenSymbol.ETH: PathDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.SPACE.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: PathDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.USDC: PathDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature='0x38ed1739'
            )
        }
    }
