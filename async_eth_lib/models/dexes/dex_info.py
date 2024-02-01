from async_eth_lib.models.contracts.raw_contract import RawContract


class DexInfo:
    contracts_dict: dict[str, dict[str, RawContract]]
    
    def __init__(
        self,
        contracts_dict: dict[str, dict[str, RawContract]]
    ) -> None:
        self.contracts_list = contracts_dict