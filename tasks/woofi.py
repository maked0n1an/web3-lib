import asyncio
from web3.types import (
    TxParams
)
from async_eth_lib.models.others.token_amount import TokenAmount
from async_eth_lib.models.transactions.tx_args import TxArgs
from data.models import Contracts
from tasks.base_task import BaseTask


class WooFi(BaseTask):
    async def swap_eth_to_usdc(
        self,
        amount: TokenAmount,
        slippage: float = 0.5
    ) -> str:
        failed_text = 'Failed swap ETH to USDC via WooFi'

        contract = await self.client.contract.get(contract_address=Contracts.ARBITRUM_WOOFI)

        from_token = Contracts.ARBITRUM_ETH
        to_token = Contracts.ARBITRUM_USDC

        eth_price = await self.get_token_price(from_token.title, to_token.title)
        min_to_amount = TokenAmount(
            amount=float(amount.Ether) * eth_price * (1 - slippage / 100),
            decimals=await self.client.contract.get_decimals(to_token.address)
        )

        args = TxArgs(
            fromToken=from_token.address,
            toToken=to_token.address,
            fromAmount=amount.Wei,
            min_to_amount=min_to_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple()),
            value=amount.Wei
        )

        tx = await self.client.contract.transaction.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_tx_receipt(account_manager=self.client.account_manager, timeout=150)

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath            
            return f'{amount.Ether} ETH was swapped to {min_to_amount.Ether} USDC via Woofi: {full_path + tx.hash.hex()}'

        return failed_text

    async def swap_usdc_to_eth(
        self,
        amount: TokenAmount | None = None,
        slippage: float = 0.4
    ) -> str:
        failed_text = f'Failed swap USDC to EHT via WooFi'
        contract = await self.client.contract.get(contract_address=Contracts.ARBITRUM_WOOFI)

        from_token = Contracts.ARBITRUM_USDC
        to_token = Contracts.ARBITRUM_ETH

        if not amount:
            amount = await self.client.contract.get_balance(
                token_address=from_token.address
            )
        
        await self.approve_interface(token_address=from_token.address, spender=contract.address, amount=amount)
        await asyncio.sleep(3)

        eth_price = await self.get_token_price(from_token.title, to_token.title)
        min_to_amount = TokenAmount(
            amount=float(amount.Ether) * eth_price * (1 - slippage / 100)
        )

        args = TxArgs(
            fromToken=from_token.address,
            toToken=to_token.address,
            fromAmount=amount.Wei,
            minToAmount=min_to_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple())
        )
        
        tx = await self.client.contract.transaction.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_tx_receipt(account_manager=self.client.account_manager)
        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath
            
            return f'{amount.Ether} USDC was swaped to {min_to_amount.Ether} ETH via WooFi: {full_path + tx.hash.hex()}'
        
        return failed_text
