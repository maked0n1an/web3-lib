from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.others.token_amount import TokenAmount


class SwapQuery:
    def __init__(
        self,
        from_token: RawContract,
        to_token: RawContract,
        from_amount: TokenAmount,
        min_to_amount: TokenAmount
    ) -> None:
        self.from_token = from_token
        self.to_token = to_token
        self.from_amount = from_amount
        self.min_to_amount = min_to_amount