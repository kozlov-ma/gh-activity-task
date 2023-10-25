import dataclasses

import aiohttp


@dataclasses.dataclass
class State:
    token: str
    client: aiohttp.ClientSession

    def headers(self):
        return {"Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"}

    def __init__(self, token: str):
        self.token = token
        self.client = aiohttp.ClientSession(headers=self.headers(),
                                            timeout=aiohttp.ClientTimeout(100))

    async def shutdown(self):
        await self.client.close()
