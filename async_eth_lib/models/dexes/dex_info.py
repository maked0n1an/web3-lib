from async_eth_lib.models.contracts.raw_contract import RawContract


class DexInfo:
    """
    An information class for a decentralized exchange (DEX).

    Attributes:
        contracts_dict (Dict[str, Dict[str, RawContract]]): A dictionary containing information about contracts.

    """
    contracts_dict: dict[str, dict[str, RawContract]]
    
    def __init__(
        self,
        contracts_dict: dict[str, dict[str, RawContract]]
    ) -> None:
        """
        Initialize the DexInfo class.

        Args:
            contracts_dict (Dict[str, Dict[str, RawContract]]): A dictionary containing information about contracts.

        """
        self.contracts_list = contracts_dict