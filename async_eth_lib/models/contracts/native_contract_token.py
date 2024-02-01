from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.dataclasses import DefaultAbis


class NativeTokenContract(RawContract):
    def __init__(
        self,
        title: str       
    ) -> None:
        super().__init__(
            title=title,
            address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
            abi=DefaultAbis.Token,
            is_native_token=True
        )
        