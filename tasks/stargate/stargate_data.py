from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.common import Singleton
from async_eth_lib.models.others.constants import CurrencySymbol
from data.models.contracts import Contracts
from tasks.stargate.models import StargateNetworkInfo, TokenData


class StargateData(Singleton):    
    networks_dict = {
        Networks.Arbitrum.name: StargateNetworkInfo(
            chain_id=110,
            token_dict={
                CurrencySymbol.USDC: TokenData(
                    token_address=Contracts.ARBITRUM_USDC.address,
                    bridge_address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                    pool_id=1
                ),
                CurrencySymbol.USDT: TokenData(
                    token_address=Contracts.ARBITRUM_USDT.address,
                    bridge_address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                    pool_id=2
                ),
                CurrencySymbol.DAI: TokenData(
                    token_address=Contracts.ARBITRUM_DAI.address,
                    bridge_address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                    pool_id=3
                ),
                CurrencySymbol.ETH: TokenData(
                    token_address=Contracts.ARBITRUM_ETH.address,
                    bridge_address='0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
                    pool_id=13
                )
            }
        ),
        Networks.Avalanche.name: StargateNetworkInfo(
            chain_id=106,
            token_dict={
                CurrencySymbol.USDC: TokenData(
                    token_address=Contracts.AVALANCHE_USDC.address,
                    bridge_address='0x002b8491765536B7D4FE3e59dB46596e1F577eCb',
                    pool_id=1
                ),
                CurrencySymbol.USDT: TokenData(
                    token_address=Contracts.AVALANCHE_USDT.address,
                    bridge_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    pool_id=2
                ),
            }
        ),
        Networks.BSC.name: StargateNetworkInfo(
            chain_id=102,
            token_dict={
                CurrencySymbol.USDT: TokenData(
                    token_address=Contracts.BSC_USDT.address,
                    bridge_address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
                    pool_id=2
                ),
                CurrencySymbol.BUSD: TokenData(
                    token_address=Contracts.BSC_BUSD.address,
                    bridge_address='0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
                    pool_id=5
                )
            }
        ),
        Networks.Fantom.name: StargateNetworkInfo(
            chain_id=112,
            token_dict={
                CurrencySymbol.USDC: TokenData(
                    token_address=Contracts.FANTOM_USDC.address,
                    bridge_address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
                    pool_id=21
                )
            }
        ),
        Networks.Optimism.name: StargateNetworkInfo(
            chain_id=111,
            token_dict={
                CurrencySymbol.USDC: TokenData(
                    token_address=Contracts.ARBITRUM_USDC.address,
                    bridge_address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
                    pool_id=1
                ),
                CurrencySymbol.DAI: TokenData(
                    token_address=Contracts.ARBITRUM_DAI.address,
                    bridge_address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
                    pool_id=3
                ),
                CurrencySymbol.ETH: TokenData(
                    token_address=Contracts.ARBITRUM_ETH.address,
                    bridge_address='0xb49c4e680174e331cb0a7ff3ab58afc9738d5f8b',
                    pool_id=13
                )
            }
        ),
        Networks.Polygon.name: StargateNetworkInfo(
            chain_id=109,
            token_dict={
                CurrencySymbol.USDC: TokenData(
                    token_address=Contracts.ARBITRUM_USDC.address,
                    bridge_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    pool_id=1
                ),
                CurrencySymbol.USDT: TokenData(
                    token_address=Contracts.ARBITRUM_USDT.address,
                    bridge_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    pool_id=2
                ),
                CurrencySymbol.DAI: TokenData(
                    token_address=Contracts.ARBITRUM_DAI.address,
                    bridge_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                    pool_id=3
                )
            }
        )
    }

    @classmethod
    def get_data(cls, network: str, token: str) -> tuple[int, TokenData] | None:
        network = network.lower()
        token = token.upper()
        
        if network in cls.networks_dict:
            network_data = cls.networks_dict[network]

            if token in network_data.token_dict:
                return (network_data.chain_id, network_data.token_dict[token])

        return None
