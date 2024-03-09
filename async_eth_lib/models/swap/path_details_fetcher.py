import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.swap.path_details import PathDetails


class PathDetailsFetcher:
    PATHS: dict[str, dict[str: PathDetails]] = {}

    @classmethod
    def get_tx_payload_details(
        cls,
        first_token: str,
        second_token: str
    ) -> PathDetails:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.PATHS:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} tx_payloads dict"
            )

        available_token_routes = cls.PATHS[first_token]

        if second_token not in available_token_routes:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {cls.__name__} {first_token} tx_payloads dict"
            )

        return available_token_routes[second_token]
