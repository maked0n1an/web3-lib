from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.route_data_fetcher import RouteDataFetcher
from async_eth_lib.models.swap.route_info import RouteInfo


class MuteRoutes(RouteDataFetcher):
    routes = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: RouteInfo(
                method_name='swapExactETHForTokensSupportingFeeOnTransferTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: RouteInfo(
                method_name='swapExactETHForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_USDT.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: RouteInfo(
                method_name='swapExactETHForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                bool_list=[False, False]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: RouteInfo(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.USDT: RouteInfo(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_USDT.address,
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.WBTC: RouteInfo(
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
            TokenSymbol.USDC: RouteInfo(
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
            TokenSymbol.ETH: RouteInfo(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: RouteInfo(
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
            TokenSymbol.ETH: RouteInfo(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: RouteInfo(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDT.address
                ],
                bool_list=[False, False, False]
            ),
            TokenSymbol.USDC: RouteInfo(
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
