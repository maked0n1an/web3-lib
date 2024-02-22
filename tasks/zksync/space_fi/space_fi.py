import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
from tasks.base_task import BaseTask
from tasks.zksync.space_fi.space_fi_routes import SpaceFiRoutes


class SpaceFi(BaseTask):
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
        self.validate_swap_inputs(
            first_arg=swap_info.from_token,
            second_arg=swap_info.to_token,
            param_type='tokens'
        )

        contract = await self.client.contract.get(
            contract=self.SPACE_FI_ROUTER
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        route_info = SpaceFiRoutes.get_route_info(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )

        to_token = TokenContracts.get_token(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )

        eth_price = await self.get_binance_ticker_price()
        if swap_info.from_token == TokenSymbol.ETH:
            amount = float(swap_query.amount_from.Ether) * eth_price \
                * (1 - swap_info.slippage / 100)
        else:
            amount = float(swap_query.amount_from.Ether) / eth_price \
                * (1 - swap_info.slippage / 100)

        min_to_amount = TokenAmount(amount=amount, decimals=to_token.decimals)

        params = TxArgs(
            minToAmount=min_to_amount.Wei,
            path=route_info.swap_path,
            to=self.client.account_manager.account.address,
            deadline=int(time.time() + 20 * 60)
        )

        list_params = params.get_list()

        if (
            swap_info.from_token != TokenSymbol.ETH
        ):
            list_params.insert(0, swap_query.amount_from.Wei)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                route_info.method_name,
                args=tuple(list_params)
            ),
            maxPriorityFeePerGas=0
        )

        data = tx_params['data']
        tx_params['data'] = route_info.function_signature + data[10:]

        if not swap_query.from_token.is_native_token:
            result = await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params
            )
            if not result:
                return 'Not enough balance'
            await sleep(8, 15)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )

        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath

            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was swapped to '
                f'{min_to_amount.Ether} {to_token.title} '
                f'via {__class__.__name__}: '
                f'{full_path + tx.hash.hex()}'
            )
