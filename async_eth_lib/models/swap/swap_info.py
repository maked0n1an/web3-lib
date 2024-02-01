class SwapInfo:
    network: str
    from_token: str
    to_token: str
    amount: float | None
    slippage: float
    
    def __init__(
        self,
        from_token: str,
        to_token: str,
        amount: float | None = None,
        slippage: float = 0.5        
    ) -> None:
        self.from_token = from_token
        self.to_token = to_token
        self.amount = amount
        self.slippage = slippage