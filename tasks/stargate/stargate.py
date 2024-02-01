from async_eth_lib.models.client import Client
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.swap.swap_info import SwapInfo
from tasks.base_task import BaseTask
from tasks.stargate.contract_data import ContractData


class Stargate(BaseTask):
    def __init__(
        self,
        client: Client
    ) -> None:
        self.client = client
        self.contract_data = ContractData
        
    def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        pass
    