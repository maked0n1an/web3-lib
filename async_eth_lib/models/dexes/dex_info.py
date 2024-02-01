from async_eth_lib.models.contracts.raw_contract import RawContract


class DexInfo:
    name: str
    contracts: dict[str, RawContract]
    
    def __init__(
        self,
        name: str,
        contracts: dict[str, RawContract]
    ) -> None:
        self.name = name
        self.contracts = contracts