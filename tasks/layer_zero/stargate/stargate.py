from web3.types import TxParams
from eth_typing import (
    HexStr
)

import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.constants import CurrencySymbol
from async_eth_lib.models.others.params_types import ParamsTypes
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import sleep
from tasks.base_task import BaseTask
from tasks.layer_zero._data.data import LayerZeroData


class Stargate(BaseTask):
    async def swap(
        self,
        swap_info: SwapInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> str:
        from_network = self.client.account_manager.network.name
        project_name = __class__.__name__

        check = self.validate_swap_inputs(
            first_arg=from_network,
            second_arg=swap_info.to_network,
            arg_type='networks'
        )
        if check:
            return check

        src_bridge_data = LayerZeroData.get_token_bridge_info(
            project=project_name,
            network=from_network,
            token_ticker=swap_info.from_token
        )

        dst_chain_id, dst_pool_id = LayerZeroData.get_chain_id_and_pool_id(
            project=project_name,
            network=swap_info.to_network,
            token_ticker=swap_info.to_token
        )

        router_contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        if dst_fee and isinstance(dst_fee, float):
            dst_network = Networks.get_network(
                network_name=swap_info.to_network
            )
            dst_fee = TokenAmount(
                amount=dst_fee,
                decimals=dst_network.decimals
            )

        lz_tx_params = TxArgs(
            dstGasForCall=0,
            dstNativeAmount=dst_fee.Wei if dst_fee else 0,
            dstNativeAddr=(
                self.client.account_manager.account.address
                if dst_fee
                else '0x0000000000000000000000000000000000000000'
            )
        )

        args = TxArgs(
            _dstChainId=dst_chain_id,
            _srcPoolId=src_bridge_data.pool_id,
            _dstPoolId=dst_pool_id,
            _refundAddress=self.client.account_manager.account.address,
            _amountLD=swap_query.amount_from.Wei,
            _minAmountLd=int(swap_query.amount_from.Wei *
                             (100 - swap_info.slippage) / 100),
            _lzTxParams=lz_tx_params.get_tuple(),
            _to=self.client.account_manager.account.address,
            _payload='0x'
        )

        value = await self._estimate_fee_for_swap(
            router_contract=router_contract,
            dst_chain_id=dst_chain_id,
            lz_tx_params=lz_tx_params
        )

        if not value:
            return f'Can not get value for ({from_network.upper()})'

        native_balance = await self.client.contract.get_balance()

        if native_balance.Wei < value.Wei:
            return f'Too low balance: balance: {native_balance.Ether}; value: {value.Ether}'

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.account_manager.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        dst_native_amount_price = 0
        if dst_fee:
            dst_token_price = await self.get_binance_ticker_price(
                first_token=dst_network.coin_symbol
            )
            dst_native_amount_price = float(dst_fee.Ether) * dst_token_price

        if network_fee - dst_native_amount_price > max_fee:
            return (
                f'Too high fee for fee: '
                f'{network_fee - dst_native_amount_price} '
                f'({from_network.upper()})'
            )

        data=router_contract.encodeABI('swap', args=args.get_tuple())

        tx_params = TxParams(
            to=router_contract.address,
            data = data,
            value=value.Wei
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=src_bridge_data.bridge_contract.address,
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

        if receipt:
            return (
                f'{swap_query.amount_from.Ether} {swap_info.from_token} '
                f'was sent from {from_network.upper()} '
                f'to {swap_info.to_network.upper()} via Stargate: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()} '
            )

    async def swapETH(
        self,
        swap_info: SwapInfo,
        max_fee: float | None = None,
        dst_fee: float | TokenAmount | None = None
    ) -> None:
        from_network = self.client.account_manager.network.name
        project_name = __class__.__name__

        check = self.validate_swap_inputs(
            first_arg=from_network,
            second_arg=swap_info.to_network,
            arg_type='networks'
        )
        if check:
            return check

        src_bridge_data = LayerZeroData.get_token_bridge_info(
            project=project_name,
            network=from_network,
            token_ticker=swap_info.from_token
        )

        dst_chain_id, dst_pool_id = LayerZeroData.get_chain_id_and_pool_id(
            project=project_name,
            network=swap_info.to_network,
            token_ticker=swap_info.to_token
        )

        router_contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        _lzTxParams = TxArgs(
            dstGasForCall=0,
            dstNativeAmount=0,
            dstNativeAddr='0x0000000000000000000000000000000000000000'
        )

        common_tx_args = TxArgs(
            _dstChainId=dst_chain_id,
            _srcPoolId=src_bridge_data.pool_id,
            _dstPoolId=dst_pool_id,
            _amountLD=swap_query.amount_from.Wei,
            _minAmountLD=int(swap_query.amount_from.Wei *
                             (100 - swap_info.slippage) / 100),
            _lzTxParams=_lzTxParams.get_tuple(),
            _to=self.client.account_manager.account.address,
            _payload='0x'
        )

        tx_args = TxArgs(
            _dstChainId=common_tx_args._dstChainId,
            _refundAddress=self.client.account_manager.account.address,
            _toAddress=self.client.account_manager.account.address,
            _amountLD=common_tx_args._amountLD,
            _minAmountLD=common_tx_args._minAmountLD
        )
        
        data=router_contract.encodeABI('swapETH', args=tx_args.get_tuple())

        value = await self._estimate_fee_for_swap(
            dst_chain_id=dst_chain_id,
            lz_tx_params=_lzTxParams,
            data='0x'
        )

        if not value:
            return f'Can not get value for ({from_network.upper()})'

        native_balance = await self.client.contract.get_balance()

        if native_balance.Wei < value.Wei:
            return f'Too low balance: balance: {native_balance.Ether}; value: {value.Ether}'

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.account_manager.network.coin_symbol
        )
        network_fee = float(value) * token_price

        # if network_fee > max_fee:
        #     return (
        #         f'Too high fee for fee: '
        #         f'{network_fee} '
        #         f'({from_network.upper()})'
        #     )

        tx_params = TxParams(
            to=router_contract.address,
            data=data,
            value=value.Wei
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=src_bridge_data.bridge_contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params,
                is_approve_infinity=False
            )
            await sleep(10, 30)

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3,
            timeout=250
        )

        if receipt:
            return (
                f'{swap_query.amount_from.Ether} {swap_info.from_token} '
                f'was sent from {from_network.upper()} '
                f'to {swap_info.to_network.upper()} via Stargate: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()} '
            )

    async def _get_estimateFee(
        self,
        router_contract: ParamsTypes.Contract,
        tx_args: TxArgs
    ) -> TokenAmount:
        router_contract = LayerZeroData.get_token_bridge_info(
            project=__class__.__name__,
            network='optimism',
            token_ticker=CurrencySymbol.USDC
        )

        result = await router_contract.functions.quoteLayerZeroFee(
            tx_args._dstChainId,
            tx_args._srcPoolId,
            tx_args._dstPoolId,
            self.client.account_manager.account.address,
            tx_args._amountLD,
            tx_args._minAmountLD,
            tx_args._lzTxParams.get_tuple(),
            self.client.account_manager.account.address,
            '0x'
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _estimate_fee_for_eth_swap(
        self,
        network: str,
        dst_chain_id: int,
        lz_tx_params: TxArgs
    ) -> TokenAmount:
        network_data = LayerZeroData.get_network_data(
            project=__class__.__name__,
            network=network
        )
        for key, value in network_data.bridge_dict.items():
            if key != CurrencySymbol.ETH:
                router = value.bridge_contract
        router_contract = await self.client.contract.get(
            contract=router
        )

        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account_manager.account.address,
            '0x',
            lz_tx_params.get_list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _estimate_fee_for_swap(
        self,
        dst_chain_id: int,
        lz_tx_params: TxArgs,
        router_contract: ParamsTypes.Contract | None = None,
        data: HexStr | None = None
    ) -> TokenAmount:
        if not router_contract:
            network = self.client.account_manager.network.name
            
            network_data = LayerZeroData.get_network_data(
                project=__class__.__name__,
                network=network
            )
            for key, value in network_data.bridge_dict.items():
                if key != CurrencySymbol.ETH:
                    router = value.bridge_contract
            if not router:
                raise exceptions.ContractNotExists(
                    f"The non-ETH Stargate Router for this {network} "
                    f"network has not been added to "
                    f"{__class__.__name__} networks dict"
                )

            router_contract = await self.client.contract.get(
                contract=router
            )

        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account_manager.account.address,
            data if data else '0x',
            lz_tx_params.get_list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)
