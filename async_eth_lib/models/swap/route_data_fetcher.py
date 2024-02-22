import async_eth_lib.models.others.exceptions as exceptions
from async_eth_lib.models.swap.route_info import RouteInfo


class RouteDataFetcher:
    routes: dict[str, dict[str: RouteInfo]] = {}

    @classmethod
    def get_route_info(
        cls,
        first_token: str,
        second_token: str
    ) -> RouteInfo:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.routes:
            raise exceptions.RouteNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} routes dict"
            )

        available_token_routes = cls.routes[first_token]

        if second_token not in available_token_routes:
            raise exceptions.RouteNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {first_token} routes dict"
            )

        return available_token_routes[second_token]
