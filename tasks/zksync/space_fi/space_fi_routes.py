from async_eth_lib.models.contracts.contracts import TokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails


class SpaceFiRoutes(TxPayloadDetailsFetcher):
    tx_payloads = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_USDT.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                function_signature="0x7ff36ab5"
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_SPACE.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address,
                    TokenContracts.ZKSYNC_WBTC.address
                ],
                function_signature='0x38ed1739'
            )
        },
        TokenSymbol.USDT: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_USDT.address,
                    TokenContracts.ZKSYNC_SPACE.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                function_signature="0x18cbafe5"
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_USDC.address,
                    TokenContracts.ZKSYNC_WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    TokenContracts.ZKSYNC_WBTC.address,
                    TokenContracts.ZKSYNC_USDC.address
                ],
                function_signature='0x38ed1739'
            )
        }
    }
