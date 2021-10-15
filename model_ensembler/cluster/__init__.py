import asyncio
import collections

Job = collections.namedtuple("Job", ["name", "state", "started", "finished"])
job_lock = asyncio.Lock()
