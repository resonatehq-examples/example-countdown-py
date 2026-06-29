from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import requests

from resonate.resonate import Resonate

if TYPE_CHECKING:
    from resonate.context import Context


async def countdown(ctx: Context, count: int, interval: float, url: str) -> None:
    for i in range(count, 0, -1):
        # Send notification (durable)
        message = f"Countdown: {i}"
        await ctx.run(notify, message, url)
        # Sleep for the specified interval (durable)
        await ctx.sleep(interval)
    # Final notification
    await ctx.run(notify, "Countdown complete", url)


async def notify(ctx: Context, message: str, url: str) -> None:
    print(f"notify: {message}", flush=True)
    response = requests.post(url, json={"message": message})
    response.raise_for_status()


async def main() -> None:
    r = Resonate(
        url=os.environ.get("RESONATE_URL", "http://localhost:8001"),
        group="countdown-worker",
    )
    r.register(countdown)
    r.register(notify)
    print("countdown worker running", flush=True)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
