import asyncio
import logging
import os

from pprint import pformat

import model_ensembler
import model_ensembler.batcher

from model_ensembler.tasks import \
    CheckException, TaskException, ProcessingException
from model_ensembler.utils import Arguments


async def run_check(func, check):
    """Run a check configuration.

    Args:
        func (callable): Async check method.
        check (dict): Check configuration.

    Raises:
        CheckException: Any exception from the called check.
    """
    result = False
    args = Arguments()

    while not result:
        try:
            logging.debug("PRE CHECK")
            ctx = model_ensembler.batcher.run_ctx.get()
            result = await func(ctx, **check.args)
            logging.debug("POST CHECK")
        except Exception as e:
            logging.exception(e)
            raise CheckException("Issues with flight checks, abandoning")

        if not result:
            logging.debug("Cannot continue, waiting {} seconds for next check".
                          format(args.check_timeout))
            await asyncio.sleep(args.check_timeout)


async def run_task(func, task):
    """Run a task configuration.

    Args:
        run_ctx (object): Context object for retrieving configuration.
        task (dict): Task configuration.

    Raises:
        TaskException: Any exception from the called task.

    Returns:
        (bool): True if task runs without exception.
    """
    try:
        args = dict() if not task.args else task.args
        ctx = model_ensembler.batcher.run_ctx.get()
        await func(ctx, **args)
    except Exception as e:
        logging.exception(e)
        raise TaskException("Issues with flight checks, abandoning")
    return True


async def run_task_items(items):
    """Run a set of task and checks.

    Run the list of tasks and check items, the configuration references the
    ``model_ensemble.tasks`` method to use and the context/configuration
    provides the arguments. TaskException and CheckException are trapped and
    rethrown as ProcessingException.

    Args:
        items (list): Tasks and checks.

    Raises:
        ProcessingException: A common exception thrown for failures in the
                            individual tasks.
    """
    try:
        ctx = model_ensembler.batcher.run_ctx.get()

        for item in items:
            func = getattr(model_ensembler.tasks, item.name)

            logging.debug("TASK CWD: {}".format(os.getcwd()))
            logging.debug("TASK CTX: {}".format(pformat(ctx)))
            logging.debug("TASK FUNC: {}".format(pformat(item)))

            if func.check:
                await run_check(func, item)
            else:
                await run_task(func, item)
    except (TaskException, CheckException) as e:
        raise ProcessingException(e)


# CORE EXECUTION FOR BATCHER
#
async def run_runner(limit, tasks):
    """Runs a list of tasks asynchronously.

    Given a particular limit, establish a semaphore and run up to limit tasks.
    Once the list of tasks is complete, return.

    Args:
        limit (int): Context object for retrieving configuration.
        tasks (list): Tasks and checks.

    Returns:
        (list): Completed tasks.
    """

    # TODO: return run task windows/info
    sem = asyncio.Semaphore(limit)

    async def sem_task(task):
        async with sem:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))
