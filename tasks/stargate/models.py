from eth_typing import ChecksumAddress
from web3 import Web3


class TokenData:
    def __init__(
        self,
        token_address: str | ChecksumAddress,
        bridge_address: str | ChecksumAddress,
        pool_id: int
    ) -> None:
        self.token_address = Web3.to_checksum_address(token_address)
        self.contract_address = Web3.to_checksum_address(bridge_address)
        self.pool_id = pool_id

class StargateNetworkInfo:
    def __init__(
        self,
        chain_id: int,
        token_dict: dict[str, TokenData],
    ) -> None:
        self.chain_id = chain_id
        self.token_list = token_dict