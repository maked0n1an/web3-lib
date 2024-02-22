from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails


class MuteRoutes(TxPayloadDetailsFetcher):
    tx_payloads = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForTokensSupportingFeeOnTransferTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_USDT.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                bool_list=[False, False]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_USDT.address,
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address,
                ],
                bool_list=[False, False, False]
            ),
        },
        TokenSymbol.USDT: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    # TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address,
                ],
                bool_list=[True,
                           #    False,
                           False
                           ]
            ),
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                bool_list=[False, True, True, False]
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDT.address
                ],
                bool_list=[False, False, False]
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                bool_list=[False, False, False]
            )
        }
    }
