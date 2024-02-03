from async_eth_lib.models.contracts.raw_contract import RawContract


class BridgeData:
    def __init__(
        self,
        token_contract: RawContract,
        bridge_contract: RawContract,
        pool_id: int
    ) -> None:
        self.token_contract = token_contract
        self.bridge_contract = bridge_contract
        self.pool_id = pool_id

class StargateNetworkInfo:
    def __init__(
        self,
        chain_id: int,
        token_dict: dict[str, BridgeData],
    ) -> None:
        self.chain_id = chain_id
        self.token_dict = token_dict