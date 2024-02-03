import asyncio
import random

from web3.contract import Contract, AsyncContract
from web3.types import TxParams

from async_eth_lib.models.client import Client
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from tasks.base_task import BaseTask
from tasks.stargate.stargate_data import StargateData


class Stargate(BaseTask):
    def __init__(
        self,
        client: Client
    ) -> None:
        self.client = client

    async def swap(
        self,
        swap_info: SwapInfo,
        max_fee: float = 1
    ) -> str:
        self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            arg_type='networks'
        )

        _, src_bridge_data = StargateData.get_token_data(
            network=self.client.account_manager.network.name,
            token=swap_info.from_token
        )
        dst_chain_id, dst_bridge_data = StargateData.get_token_data(
            network=swap_info.to_network,
            token=swap_info.to_token
        )

        dex_contract = await self.client.contract.get(contract=src_bridge_data.bridge_contract)

        amount_from = await self.calculate_amount_from_for_swap(
            from_token=src_bridge_data.token_contract,
            swap_info=swap_info
        )

        lz_tx_params = TxArgs(
            dstGasForCall=0,
            dstNativeAmount=0,
            dstNativeAddr='0x0000000000000000000000000000000000000000'
        )

        args = TxArgs(
            _dstChainId=dst_chain_id,
            _srcPoolId=src_bridge_data.pool_id,
            _dstPoolId=dst_bridge_data.pool_id,
            _refundAddress=self.client.account_manager.account.address,
            _amountLD=amount_from.Wei,
            _minAmountLd=int(amount_from.Wei * (100 - swap_info.slippage) / 100),
            _lzTxParams=lz_tx_params.get_tuple(),
            _to=self.client.account_manager.account.address,
            _payload='0x'
        )

        value = await self._get_value(
            router_contract=dex_contract,
            dst_chain_id=dst_chain_id,
            lz_tx_params=lz_tx_params
        )

        if not value:
            return f'Can not get value for ({self.client.account_manager.network.name})'

        native_balance = await self.client.contract.get_balance()

        if native_balance.Wei < value.Wei:
            return f'Too low balance: balance: {native_balance.Ether}; value: {value.Ether}'

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.account_manager.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        if network_fee > max_fee:
            return f'Too high fee: {network_fee}' \
            f'({self.client.account_manager.network.name})'

        if await self.approve_interface(
            token_address=src_bridge_data.token_contract.address,
            spender=src_bridge_data.bridge_contract.address,
            amount=amount_from,
            gas_price=swap_info.gas_price,
            gas_limit=swap_info.gas_limit
        ):
            await asyncio.sleep(random.randint(3, 6))
        else:
            return f'Failed: can not approve'

        tx_params = TxParams(
            to=dex_contract.address,
            data=dex_contract.encodeABI('swap', args=args.get_tuple()),
            value=value.Wei
        )
        
        tx_params = self.set_gas_price_and_gas_limit(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3,
            timeout=120
        )
        
        if receipt:
            return (
                f'{amount_from.Ether} {swap_info.from_token} '
                f'was sent from {self.client.account_manager.network.name.upper()} '
                f'to {swap_info.to_network.upper()} via Stargate: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()} '
            )

    async def _get_value(
        self,
        router_contract: AsyncContract | Contract,
        dst_chain_id: int,
        lz_tx_params: TxArgs
    ) -> TokenAmount:
        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account_manager.account.address,
            '0x',
            lz_tx_params.get_list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)
