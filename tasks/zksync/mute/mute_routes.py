from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails


class MuteRoutes(TxPayloadDetailsFetcher):
    tx_payloads = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForTokensSupportingFeeOnTransferTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.USDT.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                bool_list=[False, False]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.USDT.address,
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address,
                ],
                bool_list=[False, False, False]
            ),
        },
        TokenSymbol.USDT: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    # TokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address,
                ],
                bool_list=[True,
                           #    False,
                           False
                           ]
            ),
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                bool_list=[False, True, True, False]
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDT.address
                ],
                bool_list=[False, False, False]
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                bool_list=[False, False, False]
            )
        }
    }
