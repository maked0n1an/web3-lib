from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.contracts.contracts import TokenContracts


class BridgeData:
    def __init__(
        self,
        token_contract: TokenContracts,
        bridge_contract: RawContract,
        pool_id: int | None = None
    ) -> None:
        self.token_contract = token_contract
        self.bridge_contract = bridge_contract
        self.pool_id = pool_id
