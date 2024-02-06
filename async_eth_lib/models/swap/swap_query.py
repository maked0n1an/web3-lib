from async_eth_lib.models.contracts.raw_contract import TokenContract
from async_eth_lib.models.others.token_amount import TokenAmount


class SwapQuery:
    """
    A class representing a swap query.

    Attributes:
        from_token (RawContract): The contract of the token to swap from.
        to_token (RawContract): The contract of the token to swap to.
        from_amount (TokenAmount): The amount of the 'from' token.
        min_to_amount (TokenAmount): The minimum amount of the 'to' token.

    """

    def __init__(
        self,
        from_token: TokenContract,
        to_token: TokenContract,
        from_amount: TokenAmount,
        min_to_amount: TokenAmount | None = None
    ) -> None:
        """
        Initialize the SwapQuery class.

        Args:
            from_token (RawContract): The contract of the token to swap from.
            to_token (RawContract): The contract of the token to swap to.
            from_amount (TokenAmount): The amount of the from token.
            min_to_amount (TokenAmount): The minimum amount of the to token.

        """
        self.from_token = from_token
        self.to_token = to_token
        self.from_amount = from_amount
        self.min_to_amount = min_to_amount
