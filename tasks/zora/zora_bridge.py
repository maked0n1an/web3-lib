from aiohttp import ClientError, ClientResponse, ClientSession
import requests
from web3.types import TxParams

from async_eth_lib.models.networks.networks import Networks
from async_eth_lib.models.swap.swap_info import SwapInfo
from async_eth_lib.utils.helpers import read_json
from tasks.base_task import BaseTask


class ZoraBridge(BaseTask):
    contracts_dict = {
        'instant_deposit': {
            Networks.Zora.name: '0xf70da97812cb96acdf810712aa562db8dfa3dbef'
        },
        'instant_withdraw': {
            Networks.Ethereum.name: '0xf70da97812CB96acDF810712Aa562db8dfA3dbEF'
        }
    }

    async def deposit(
        self,
        swap_info: SwapInfo
    ) -> str:
        self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        headers = {
            'authority': 'api-zora.reservoir.tools',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.9,de-DE;q=0.8,de;q=0.7,ru-RU;q=0.6,ru;q=0.5,en-US;q=0.4',
            'content-type': 'application/json',
            'origin': 'https://bridge.zora.energy',
            'referer': 'https://bridge.zora.energy/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-rkc-version': '1.11.2',
        }
        address = self.client.account_manager.account.address
        contract_address, _ = await self.client.contract.get_contract_attributes(
            contract=self.contracts_dict['instant_deposit'][swap_info.to_network]
        )
        value = swap_query.amount_from

        json_data = {
            'user': address,
            'txs': [
                {
                    'to': address,
                    'value': value.Wei,
                    'data': '0x',
                },
            ],
            'originChainId': self.client.account_manager.network.chain_id,
        }

        response = requests.post(
            'https://api-zora.reservoir.tools/execute/call/v1', headers=headers, json=json_data)

        if response:
            json_response = await response.json()

            data = json_response['steps']['items']['data']['data']

        tx_params = TxParams(
            to=contract_address,
            data=data,
            value=value.Wei
        )

        # fee = await self.client.contract.transaction.get_estimate_gas(
        #     tx_params=tx_params
        # )

        # tx_params['value'] -= 10000 * fee.Wei

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )

        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath

            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was bridged to '
                f'{swap_info.to_network.capitalize()} '
                f'via {__class__.__name__}: '
                f'{full_path + tx.hash.hex()}'
            )

    async def withdraw(
        self,
        swap_info: SwapInfo
    ) -> str:
        self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        headers = {
            'authority': 'api-zora.reservoir.tools',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en;q=0.9,de-DE;q=0.8,de;q=0.7,ru-RU;q=0.6,ru;q=0.5,en-US;q=0.4',
            'content-type': 'application/json',
            'origin': 'https://bridge.zora.energy',
            'referer': 'https://bridge.zora.energy/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-rkc-version': '1.11.2',
        }
        
        contract_address, _ = await self.client.contract.get_contract_attributes(
            contract=self.contracts_dict['instant_withdraw'][swap_info.to_network]
        )
        address = self.client.account_manager.account.address
        value = swap_query.amount_from
        url = 'https://api-zora.reservoir.tools/execute/call/v1'
        
        json_data = {
            'user': address,
            'txs': [
                {
                    'to': address,
                    'value': str(value.Wei),
                    'data': '0x',
                },
            ],
            'originChainId': self.client.account_manager.network.chain_id,
        }
        response = await self._make_request("POST", url=url, headers=headers, json_data=json_data)

        if response.status == 200:
            json_response = await response.json()

            data = json_response['steps'][0]['items'][0]['data']['data']

        tx_params = TxParams(
            to=contract_address,
            data=data,
            value=value.Wei
        )
        
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        # fee = await self.client.contract.transaction.get_estimate_gas(
        #     tx_params=tx_params
        # )

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )

        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath

            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was bridged to '
                f'{swap_info.to_network.capitalize()} '
                f'via {__class__.__name__}: '
                f'{full_path + tx.hash.hex()}'
            )

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: dict,
        json_data: dict = {}
    ) -> ClientResponse:
        try:
            async with ClientSession() as session:
                response = await session.request(
                    method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    proxy=self.client.account_manager.proxy,
                    timeout=200
                )

                return response
        except ClientError as e:
            print(f"An error occured: {e}")
