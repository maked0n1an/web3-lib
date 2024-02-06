from async_eth_lib.models.bridges.bridge_data import BridgeData


class LayerZeroNetworkInfo:
    def __init__(
        self,
        chain_id: int,
        token_dict: dict[str, BridgeData],
    ) -> None:
        self.chain_id = chain_id
        self.token_dict = token_dict
