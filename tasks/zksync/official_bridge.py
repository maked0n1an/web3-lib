import json
from web3 import Web3
from web3.types import TxParams

from async_eth_lib.models.client import Client
from async_eth_lib.models.contracts.contracts import ZkSyncTokenContracts
from async_eth_lib.models.contracts.raw_contract import RawContract
from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.others.constants import LogStatus
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.models.transactions.tx_args import TxArgs
from async_eth_lib.utils.helpers import read_json
from tasks._common.swap_task import SwapTask

ZKSYNC_OFFICIAL_BRIDGE = [
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "address",
                "name": "_l1Receiver", 
                "type": "address"
            },
        ],
        "name": "withdraw",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    }
]

class OfficialBridge(SwapTask):    
    ETH_OFFICIAL_BRIDGE = RawContract(
        title='ETH_OFFICIAL_BRIDGE',
        address='0x32400084c286cf3e17e7b677ea9583e60a000324',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'official_bridge.json')
        )
    )
    
    ZKSYNC_OFFICIAL_BRIDGE = RawContract(
        title='ZKSYNC_OFFICIAL_BRIDGE',
        address='0x000000000000000000000000000000000000800A',
        abi=json.dumps(ZKSYNC_OFFICIAL_BRIDGE)
    )
    
    async def deposit(
        self, 
        swap_info: SwapInfo
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type="networks",
            function='deposit'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        eth_client = Client(
            private_key=self.client.account_manager.account.key,
            network=Networks.Ethereum
        )        
        contract = await eth_client.contract.get(contract=self.ETH_OFFICIAL_BRIDGE)
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)
        
        balance = await eth_client.contract.get_balance()
        gas_price = await eth_client.contract.transaction.get_gas_price()
        gas_limit = 134_886
        l2_gas_limit = 397_207

        transaction_fee = TokenAmount(
            amount=gas_price.Wei * gas_limit,
            wei=True
        )

        if swap_query.amount_from.Wei >= balance.Wei:
            swap_query.amount_from = TokenAmount(
                amount=balance.Wei - transaction_fee.Wei * 1.2,
                wei=True
            )

        if swap_query.amount_from.Wei < 0:
            message = 'too low ETH balance; ETH balance: {balance.Ether}; ' \
                   f'transaction fee: {transaction_fee.Ether}'
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.FAILED, message=message
            )
        
            return False

        # https://docs.zksync.io/build/tutorials/how-to/send-transaction-l1-l2.html#step-by-step
        max_fee = TokenAmount(
            amount=int(await contract.functions.l2TransactionBaseCost(
                gas_price.Wei, 
                l2_gas_limit, 
                800
            ).call() * 1.05),
            wei=True
        )

        if balance.Wei < swap_query.amount_from.Wei + transaction_fee.Wei + max_fee.Wei:
            message = 'insufficient balance'
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.FAILED, message=message
            )
        
            return False

        args = TxArgs(
            _contractL2=eth_client.account_manager.account.address,
            _l2Value=swap_query.amount_from.Wei,
            _calldata=eth_client.account_manager.w3.to_bytes(text=''),
            _l2GasLimit=l2_gas_limit,
            _l2GasPerPubdataByteLimit=800,
            _factoryDeps=[],
            _refundRecipient=eth_client.account_manager.account.address,
        )

        max_priority_fee_per_gas = Web3.to_wei(1.5, 'gwei')
        tx_params = TxParams(
            maxPriorityFeePerGas=max_priority_fee_per_gas,
            maxFeePerGas=await eth_client.contract.transaction.get_base_fee() + max_priority_fee_per_gas,
            to=contract.address,
            data=contract.encodeABI('requestL2Transaction', args=args.get_tuple()),
            value=swap_query.amount_from.Wei + max_fee.Wei
        )

        try:
            receipt_status, log_status, message = await self.perform_bridge(tx_params)
            
            self.client.account_manager.custom_logger.log_message(log_status,message)

            return receipt_status
        except Exception as e:
            error = str(e)
            insufficient_funds = 'insufficient funds for gas + value'
            if insufficient_funds in error:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=insufficient_funds.capitalize()
                )
            else:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=error
                )
        return False
    
    async def withdraw(
        self, 
        swap_info: SwapInfo
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type="networks",
            function='withdraw'
        )
        if check_message:
            error_message=check_message
            
        elif self.client.account_manager.network.name != Networks.ZkSync.name:
            error_message=f'wrong network ({self.client.account_manager.network.name})'

        if error_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=error_message
            )

            return False

        contract = await self.client.contract.get(
            contract=self.ZKSYNC_OFFICIAL_BRIDGE
        )
        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )
        
        args = TxArgs(
            _l1Receiver=self.client.account_manager.account.address
        )
        
        tx_params = TxParams(
            maxPriorityFeePerGas=Web3.to_wei(0.25, 'gwei'),
            maxFeePerGas=Web3.to_wei(0.25, 'gwei'),
            to=contract.address,
            data=contract.encodeABI('withdraw', args=args.get_tuple()),
            value=swap_query.amount_from.Wei
        )
        
        try:
            receipt_status, log_status, message = await self.perform_bridge(tx_params)
            
            self.client.account_manager.custom_logger.log_message(log_status,message)

            return receipt_status
        except Exception as e:
            error = str(e)
            insufficient_funds = 'insufficient funds for gas + value'
            if insufficient_funds in error:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=insufficient_funds.capitalize()
                )
            else:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=error
                )
        return False