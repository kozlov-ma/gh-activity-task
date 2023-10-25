import asyncio
import json
import math
import re
from collections import Counter
from http import HTTPStatus

from loguru import logger

from main import PAGE_COUNT_REGEX
from state import State
from repos import Repository
from utils import counter_sum


async def commits_total(st: State, repo: Repository) -> int:
    async with st.client.get(repo.actual_commits_url(),
                             params={'per_page': 1}) as resp:
        if resp.status == HTTPStatus.OK:
            count = int(re.findall(PAGE_COUNT_REGEX, resp.headers['Link'])[-1])
            return count
        else:
            logger.error(
                f"Couldn't get info about commits in '{repo.full_name} (HTTP "
                f"Status: {resp.status})'")
            return 0


async def count_authors_for_page(st: State, repo: Repository, page: int,
                                 per_page: int = 100) -> Counter:
    authors = Counter()
    async with st.client.get(repo.actual_commits_url(), params={'page': page,
                                                                'per_page': per_page}) as resp:
        if resp.status == HTTPStatus.OK:
            body = json.loads(await resp.text())
            for commit in body:
                commit = commit['commit']
                if commit['message'].startswith("Merge pull request #"):
                    continue

                authors[commit['author']['email']] += 1

            await asyncio.sleep(1)  # lots of 403s, hope this helps
            return authors
        else:
            logger.error(
                f"Couldn't receive commits for '{repo.full_name}', page {page}, {per_page} per page. (HTTP Status: {resp.status})")
            return Counter()


async def count_repo_authors(st: State, repo: Repository) -> Counter:
    logger.info(f"Counting commits in '{repo.full_name}'")
    tasks = []
    for page in range(0, math.ceil(await commits_total(st, repo) / 100)):
        tasks.append(count_authors_for_page(st, repo, page, 100))

    authors = counter_sum(await asyncio.gather(*tasks))
    logger.info(
        f"Found {len(authors)} authors in '{repo.full_name}'. {sum(authors.values())} contributions in total")

    return authors
