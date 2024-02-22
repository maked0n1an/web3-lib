import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.swap.tx_payload_details import TxPayloadDetails


class TxPayloadDetailsFetcher:
    tx_payloads: dict[str, dict[str: TxPayloadDetails]] = {}

    @classmethod
    def get_tx_payload_details(
        cls,
        first_token: str,
        second_token: str
    ) -> TxPayloadDetails:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.tx_payloads:
            raise exceptions.RouteNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} routes dict"
            )

        available_token_routes = cls.tx_payloads[first_token]

        if second_token not in available_token_routes:
            raise exceptions.RouteNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {first_token} routes dict"
            )

        return available_token_routes[second_token]
