import asyncio
import dataclasses
import json
import math
import re
from http import HTTPStatus

from loguru import logger

from main import PAGE_COUNT_REGEX
from state import State
from utils import flatten


@dataclasses.dataclass
class Repository:
    full_name: str
    commits_url: str

    def actual_commits_url(self):
        return self.commits_url.split('{')[0]


async def repos_total(st: State, org_name: str) -> int:
    url = f"https://api.github.com/orgs/{org_name}/repos"
    async with st.client.get(url, params={'per_page': 1}) as resp:
        if resp.status == HTTPStatus.OK:
            count = int(re.findall(PAGE_COUNT_REGEX, resp.headers['Link'])[-1])
            return count
        else:
            logger.error(f"Couldn't get info about repositories (HTTP Status: {resp.status})")
            return 0


async def repos_for_page(st: State, org_name: str, page: int,
                         per_page: int = 100) -> list[Repository]:
    url = f"https://api.github.com/orgs/{org_name}/repos"
    repos = []
    async with st.client.get(url, params={'page': page,
                                          'per_page': per_page}) as resp:
        if resp.status == HTTPStatus.OK:
            body = json.loads(await resp.text())
            for repo in body:
                repos.append(Repository(repo['full_name'], repo['commits_url']))

            return repos
        else:
            raise RuntimeError(
                f"Couldn't receive repositories for {org_name}, page {page}, {per_page} per page. (HTTP Status: {resp.status})")


async def repos(st: State, org_name: str) -> list[Repository]:
    tasks = []
    for page in range(0, math.ceil(await repos_total(st, org_name) / 100)):
        tasks.append(repos_for_page(st, org_name, page, 100))

    res = flatten(await asyncio.gather(*tasks))
    logger.info(f"Got info about {len(res)} repositories of '{org_name}'")
    return res
