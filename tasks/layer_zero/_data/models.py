from async_eth_lib.models.bridges.bridge_data import TokenBridgeInfo


class LayerZeroNetworkData:
    def __init__(
        self,
        chain_id: int,
        bridge_dict: dict[str, TokenBridgeInfo],
    ) -> None:
        self.chain_id = chain_id
        self.bridge_dict = bridge_dict
