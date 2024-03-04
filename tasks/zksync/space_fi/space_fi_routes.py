from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.others.constants import TokenSymbol
from async_eth_lib.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails


class SpaceFiRoutes(TxPayloadDetailsFetcher):
    tx_payloads = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDT.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                function_signature="0x7ff36ab5"
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.SPACE.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                function_signature='0x38ed1739'
            )
        },
        TokenSymbol.USDT: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.SPACE.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                function_signature='0x38ed1739'
            )
        }
    }
