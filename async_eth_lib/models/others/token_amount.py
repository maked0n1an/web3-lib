from decimal import Decimal


class TokenAmount:
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(
        self,
        amount: int | float | Decimal | str,
        decimals: int = 18,
        wei: bool = False
    ) -> False:
        if wei:
            self.Wei: int = int(amount)
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals
        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def __str__(self) -> str:
        return f'{self.Wei}'
