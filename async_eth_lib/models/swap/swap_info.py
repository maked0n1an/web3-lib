import random


class SwapInfo:
    """
    A class representing information for a token swap.

    Attributes:
        from_token (str): The token to swap from.
        to_token (str): The token to swap to.
        amount (float | None): The amount to swap (default is None).
        slippage (float): The slippage tolerance (default is 0.5).
        amount_by_percent (float): The amount calculated based on a percentage (default is 0).
        multiplier_of_gas (int): A multiplier for gas calculation (default is None).

    """
    from_network: str
    to_network: str
    from_token: str
    to_token: str
    amount: float
    slippage: float

    def __init__(
        self,
        from_token: str,
        to_token: str,
        amount: float | None = None,
        slippage: float = 0.5,
        from_amount: float | None = None,
        to_amount: float | None = None,
        decimals: int = 5,
        all_amount: bool = False,
        min_percent: int | None = None,
        max_percent: int | None = None,
        multiplier_of_gas: int | None = None
    ) -> None:
        """
        Initialize the SwapInfo class.

        Args:
            from_token (str): The token to swap from.
            to_token (str): The token to swap to.
            amount (float | None): The amount to swap (default is None).
            slippage (float): The slippage tolerance (default is 0.5).
            from_amount (float | None): The minimum amount for random amount generation.
            to_amount (float | None): The maximum amount for random amount generation.
            decimals (int): The number of decimal places for random amount generation (default is 5).
            all_amount (bool): If True, indicates to use the entire amount for the swap (default is False).
            min_percent (int | None): The minimum percentage for random amount generation.
            max_percent (int | None): The maximum percentage for random amount generation.
            multiplier_of_gas (int | None): A multiplier for gas calculation (default is None).

        """
        self.from_token = from_token
        self.to_token = to_token
        self.amount = amount
        self.slippage = slippage
        self.amount_by_percent = 0
        self.multiplier_of_gas = multiplier_of_gas
        if from_amount and to_amount:
            self.amount = self._get_random_amount(
                from_amount, to_amount, decimals=decimals)
        if all_amount:
            self.all_amount = all_amount
        if min_percent and max_percent:
            self.amount_by_percent = self._get_random_amount_by_percent(
                min_percent, max_percent
            )

    def _get_random_amount(self, from_amount: float, to_amount: float, decimals: int):
        random_amount = round(random.uniform(from_amount, to_amount), decimals)
        return random_amount

    def _get_random_amount_by_percent(self, min_percent: int, max_percent: int):
        random_percent_amount = random.randint(min_percent, max_percent) / 100
        return random_percent_amount
