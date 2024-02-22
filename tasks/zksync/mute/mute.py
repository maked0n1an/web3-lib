import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.swap.route_info import RouteInfo
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.swap.swap_query import SwapQuery
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json, sleep
from tasks.base_task import BaseTask
from tasks.zksync.mute.mute_routes import MuteRoutes


class Mute(BaseTask):
    MUTE_UNIVERSAL = RawContract(
        title='Mute',
        address='0x8b791913eb07c32779a16750e3868aa8495f5964',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'mute','abi.json')
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
            contract=self.MUTE_UNIVERSAL
        )

        swap_query = await self._create_swap_query(
            contract=contract,
            swap_info=swap_info
        )

        route_info = MuteRoutes.get_route_info(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )

        params = TxArgs(
            amountOutMin=swap_query.min_to_amount.Wei,
            path=route_info.swap_path,
            to=self.client.account_manager.account.address,
            deadline=int(time.time() + 20 * 60),
            stable=route_info.bool_list
        )

        tuple_params = params.get_list()

        if (
            swap_info.from_token != TokenSymbol.ETH
        ):
            tuple_params.insert(0, swap_query.amount_from.Wei)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                route_info.method_name,
                args=tuple(tuple_params)
            ),
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
                return 'Not enough balance'
            await sleep(8, 15)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3, timeout=300
        )
        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath

            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was swapped to '
                f'{swap_query.min_to_amount.Ether} {swap_query.to_token.title} '
                f'via {__class__.__name__}: '
                f'{full_path + tx.hash.hex()}'
            )

        return 'Failed swap'

    async def _create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo
    ) -> SwapQuery:
        network = self.client.account_manager.network.name
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)

        if swap_info.from_token == TokenSymbol.ETH:
            from_token_symbol=TokenSymbol.WETH
        else:
            from_token_symbol=swap_info.from_token

        if swap_info.to_token == TokenSymbol.ETH:
            to_token_symbol=TokenSymbol.WETH
        else:
            to_token_symbol=swap_info.to_token
        
        from_token = TokenContracts.get_token(
            network_name=network,
            token_symbol=from_token_symbol
        )
        
        swap_query.to_token = TokenContracts.get_token(
            network_name=network,
            token_symbol=to_token_symbol
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
