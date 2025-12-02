from resonategcp import Resonate
from .countdown import countdown

resonate = Resonate.remote()

resonate.register(countdown)

handler = resonate.handler_http()