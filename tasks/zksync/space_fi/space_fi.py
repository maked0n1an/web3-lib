import time

from web3.types import TxParams

from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json
from tasks.base_task import BaseTask


class SpaceFi(BaseTask):
    SPACE_FI_ROUTER = RawContract(
        title='SpaceFiRouter',
        address='0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'space_fi','abi.json')
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
        
        to_token = TokenContracts.get_token(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )
        
        eth_price = await self.get_binance_ticker_price()
        amount_out_min = TokenAmount(
            amount=float(swap_query.amount_from.Ether) * eth_price 
                * (1 - swap_info.slippage / 100),
            decimals=to_token.decimals
        )
                
        params = TxArgs(
            amountOut=amount_out_min.Wei,
            path=[
                TokenContracts.ZKSYNC_WETH.address,
                TokenContracts.ZKSYNC_USDC.address
            ],
            to=self.client.account_manager.account.address,
            deadline=int(time.time() + 20 * 60),
        )
        
        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'noName',
                args=params.get_tuple()
            ),
            maxPriorityFeePerGas=0
        )
        
        data=tx_params['data']
        tx_params['data'] = '0x7ff36ab5' + data[10:]
        
        if swap_query.from_token.is_native_token:
            tx_params['value'] = swap_query.amount_from.Wei
        
        BaseTask.parse_params(
            params=tx_params['data']
        )
        return 'nice'