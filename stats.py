import asyncio
from collections import Counter

from loguru import logger

from commits import count_repo_authors
from state import State
from repos import repos
from utils import counter_sum


async def stat(st: State, org_name: str) -> Counter:
    tasks = []
    for repo in await repos(st, org_name):
        tasks.append(count_repo_authors(st, repo))

    stats = counter_sum(await asyncio.gather(*tasks))
    logger.info(f"Collected stats about {len(stats)} authors")
    return stats


async def cli_stat(st: State, n_authors: int, org_name: str):
    stats = await stat(st, org_name)
    for (author, contribs) in stats.most_common(n_authors):
        print(f"{author} : {contribs}")


async def gui_stat(st: State, n_authors: int, org_name: str):
    pass
