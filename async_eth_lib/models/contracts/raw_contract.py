import json

from web3 import Web3
from typing import Any
from eth_typing import ChecksumAddress
from async_eth_lib.models.others.common import AutoRepr


class RawContract(AutoRepr):
    """
    An instance of a raw contract.

    Attributes:
        title (str): a contract title.
        address (ChecksumAddress): a contract address.
        abi (list[dict[str, Any]] | str): an ABI of the contract.
        is_native_token (bool): is this contract native token of network (False)

    """
    title: str
    address: ChecksumAddress
    abi: list[dict[str, Any]]
    is_native_token: bool

    def __init__(
        self,
        title: str,
        address: str,
        abi: list[dict[str, Any]] | str,
        is_native_token: bool = False
    ) -> None:
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi (Union[List[Dict[str, Any]], str]): an ABI of the contract.
            is_native_token (bool): is this contract native token of network (False)
        """
        self.title = title
        self.address = Web3.to_checksum_address(address)
        self.abi = json.loads(abi) if isinstance(abi, str) else abi
        self.is_native_token = is_native_token