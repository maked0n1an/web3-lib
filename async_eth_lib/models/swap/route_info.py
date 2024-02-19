from typing import List


class RouteInfo:
    def __init__(
        self,
        method_name: str,
        addresses: List[str],
        bool_list: List[bool] | None = None
    ):
        self.method_name = method_name
        self.swap_route = addresses
        if bool_list:
            self.bool_list = bool_list