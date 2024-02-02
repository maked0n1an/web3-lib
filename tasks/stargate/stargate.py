from async_eth_lib.models.client import Client
from async_eth_lib.models.swap.swap_info import SwapInfo
from tasks.base_task import BaseTask
from tasks.stargate.models import StargateNetworkInfo

class Stargate(BaseTask):
    def __init__(
        self,
        client: Client
    ) -> None:
        self.client = client
        self.contract_data = StargateNetworkInfo()
        
    def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        pass
    