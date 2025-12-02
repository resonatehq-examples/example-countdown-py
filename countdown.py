from resonate import Resonate, Context
from typing import Generator, Any
import requests

resonate = Resonate.remote()


def countdown(ctx: Context, count: int, interval, url: str) -> Generator[Any, Any, Any]:
    for i in range(count, 0, -1):
        # Send notification
        message = f"Countdown: {i}"
        yield ctx.run(notify, message=message, url=url)
        # Sleep for the specified interval
        yield ctx.sleep(interval)
    # Final notification
    yield ctx.run(notify, message="Countdown complete", url=url)


def notify(_: Context, message: str, url: str) -> None:
    response = requests.post(url, json={"message": message})
    response.raise_for_status()


resonate.start()



