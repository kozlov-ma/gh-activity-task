import asyncio
import os
import re

import click
import loguru

import state
import stats
import rate_limit

PAGE_COUNT_REGEX = re.compile('(?<=&page=)\d+')


@click.command()
@click.argument("org_name", type=click.STRING, default="charmbracelet")
@click.argument("n_authors", type=click.INT, default=100)
@click.option("--show-graph", is_flag=True)
def main(org_name, n_authors, show_graph):
    asyncio.run(async_main(org_name, n_authors, show_graph))


async def async_main(org_name, n_authors, show_graph):
    token = os.environ.get("GITHUB_TOKEN")
    if token is None:
        loguru.logger.error("Must provide 'GITHUB_TOKEN' environment variable.")
        return

    st = state.State(token)

    rl = await rate_limit.rate_limit(st)
    if rl.remaining <= 0:
        loguru.logger.error(
            f"All rate limit was used. Resets after {rl.minutes_to_reset()} minutes.")
        return
    else:
        loguru.logger.info(rl)

    if show_graph:
        await (stats.gui_stat(st, n_authors, org_name))
    else:
        await (stats.cli_stat(st, n_authors, org_name))

    await st.shutdown()


if __name__ == "__main__":
    main()
