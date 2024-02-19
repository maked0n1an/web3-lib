import async_eth_lib.models.others.exceptions as exceptions

from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.route_info import RouteInfo


class MuteRoutes:
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
        },
        TokenSymbol.USDT: {
            TokenSymbol.USDC: RouteInfo(
                method_name='swapExactTokensForTokens',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    TokenContracts.ZKSYNC_USDC.address,
                ],
                bool_list=[True, False]
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
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                bool_list=[False, False]
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
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_USDT.address
                ],
                bool_list=[False, True, True, False]
            )
        }
    }

    @classmethod
    def get_route_info(
        cls,
        first_token: str,
        second_token: str
    ) -> RouteInfo:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.routes:
            raise exceptions.RouteNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} routes dict"
            )

        available_token_routes = cls.routes[first_token]

        if second_token not in available_token_routes:
            raise exceptions.RouteNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {first_token} routes dict"
            )

        return available_token_routes[second_token]
