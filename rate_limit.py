import dataclasses
import json
import math
import time
from http import HTTPStatus

from state import State


@dataclasses.dataclass
class RateLimit:
    limit: int
    used: int
    remaining: int
    reset: int

    def minutes_to_reset(self) -> int:
        return math.ceil((self.reset - time.time()) / 60)

    def __str__(self) -> str:
        return f"Rate limit: {self.used}/{self.limit} used. {self.remaining} remaining. Resets in {self.minutes_to_reset()} minutes."


async def rate_limit(st: State) -> RateLimit:
    url = "https://api.github.com/rate_limit"
    async with st.client.get(url) as resp:
        if resp.status == HTTPStatus.OK:
            body = json.loads(await resp.text())
            return RateLimit(**body['resources']['core'])
        else:
            raise RuntimeError("Couldn't get Rate Limit..")
