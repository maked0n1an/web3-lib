import random


class SwapInfo:
    network: str
    from_token: str
    to_token: str
    amount: float
    slippage: float

    def __init__(
        self,
        from_token: str,
        to_token: str,
        amount: float = 0,
        slippage: float = 0.5,
        from_amount: float | None = None,
        to_amount: float | None = None,
        decimals: int = 5,
        all_amount: bool = False,
        min_percent: int | None = None,
        max_percent: int | None = None
    ) -> None:
        self.from_token = from_token
        self.to_token = to_token
        self.amount = amount
        self.slippage = slippage
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
