from typing import List


class RouteInfo:
    def __init__(
        self,
        method_name: str,
        addresses: List[str],
        bool_list: List[bool] | None = None
    ):
        """
        Initialize the RouteInfo class.

        Args:
            method_name (str): The name of the method.
            addresses (List[str]): The list of addresses.
            bool_list (List[bool] | None): The list of boolean values (default is None).

        """
        self.method_name = method_name
        self.swap_route = addresses
        if bool_list:
            self.bool_list = bool_list