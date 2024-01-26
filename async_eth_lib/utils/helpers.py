from aiohttp import (
    ClientSession
)

import async_eth_lib.utils.exceptions as exceptions


async def make_request(
    method: str,
    url: str,
    headers: dict | None = None,
    **kwargs
) -> dict | None:
    async with ClientSession(headers=headers) as session:
        response = await session.request(method, url=url, **kwargs)

        status_code = response.status
        if status_code <= 201:
            json_response = await response.json()

            return json_response

        raise exceptions.HTTPException(
            response=response, status_code=status_code)
