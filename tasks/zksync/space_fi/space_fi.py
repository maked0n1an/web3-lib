import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContractFetcher
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
        account_address = self.client.account_manager.account.address

        contract = await self.client.contract.get(
            contract=self.SPACE_FI_ROUTER
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        tx_payload_details = SpaceFiRoutes.get_tx_payload_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )

        to_token = TokenContractFetcher.get_token(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )

        from_token_price = await self.get_binance_ticker_price(
            first_token=swap_info.from_token
        )

        if swap_query.from_token.is_native_token:
            amount = float(swap_query.amount_from.Ether) * from_token_price \
                * (1 - swap_info.slippage / 100)
        else:
            second_token_price = await self.get_binance_ticker_price(
                first_token=swap_info.to_token
            )

            amount = float(swap_query.amount_from.Ether) * from_token_price \
                / second_token_price * (1 - swap_info.slippage / 100)

        min_to_amount = TokenAmount(amount=amount, decimals=to_token.decimals)

        if swap_info.from_token != TokenSymbol.ETH:
            memory_address = 128 + 32
        else:
            memory_address = 128

        data = [
            f'{tx_payload_details.function_signature}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(min_to_amount.Wei))}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(memory_address))}',
            f'{self.to_cut_hex_prefix_and_zfill(str(account_address).lower())}',
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
