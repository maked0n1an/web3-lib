from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.dataclasses import DefaultAbis


class NativeTokenContract(RawContract):
    """
    An instance of a native token contract.

    Attributes:
        title (str): The title or name of the native token.

    """
    def __init__(
        self,
        title: str       
    ) -> None:
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.

        """
        super().__init__(
            title=title,
            address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            abi=DefaultAbis.Token,
            is_native_token=True
        )
        