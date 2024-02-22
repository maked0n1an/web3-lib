from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.route_data_fetcher import RouteDataFetcher
from async_eth_lib.models.swap.route_info import RouteInfo


class SpaceFiRoutes(RouteDataFetcher):
    routes = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: RouteInfo(
                method_name='swapExactETHForToken',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                function_signature="0x7ff36ab5"
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: RouteInfo(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_SPACE.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                function_signature="0x18cbafe5"
            )
        }
    }
