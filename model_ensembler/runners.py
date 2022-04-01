import asyncio
import contextvars
import logging
import os

from pprint import pformat

import model_ensembler

from model_ensembler.tasks import \
    CheckException, TaskException, ProcessingException
from model_ensembler.utils import Arguments


async def run_check(ctx, func, check):
    """Run a check configuration

    Args:
        ctx (object): context object for retrieving configuration
        func (callable): async check method
        check (dict): check configuration

    Raises:
        CheckException: any exception from the called check
    """
    result = False
    args = Arguments()

    while not result:
        try:
            logging.debug("PRE CHECK")
            run_ctx = ctx.get()
            result = await func(run_ctx, **check.args)
            logging.debug("POST CHECK")
        except Exception as e:
            logging.exception(e)
            raise CheckException("Issues with flight checks, abandoning")

        if not result:
            logging.debug("Cannot continue, waiting {} seconds for next check".
                          format(args.check_timeout))
            await asyncio.sleep(args.check_timeout)


async def run_task(ctx, func, task):
    """Run a task configuration

    Args:
        ctx (object): context object for retrieving configuration
        func (callable): async task method
        task (dict): task configuration

    Raises:
        TaskException: any exception from the called task
    """
    try:
        args = dict() if not task.args else task.args
        run_ctx = ctx.get()
        await func(run_ctx, **args)
    except Exception as e:
        logging.exception(e)
        raise TaskException("Issues with flight checks, abandoning")
    return True


async def run_task_items(items):
    """Run a set of task and checks

    Run the list of tasks and check items, the configuration references the
    ``model_ensemble.tasks`` method to use and the context/configuration
    provides the arguments. TaskException and CheckException are trapped and
    rethrown as ProcessingException

    Args:
        ctx (object): context object for retrieving configuration
        items (list): a list of tasks and checks

    Raises:
        ProcessingException: a common exception thrown for failures in the
        individual tasks
    """
    try:
        ctx = contextvars.copy_context().get("ctx")

        for item in items:
            func = getattr(model_ensembler.tasks, item.name)

            logging.debug("TASK CWD: {}".format(os.getcwd()))
            logging.debug("TASK CTX: {}".format(pformat(ctx.get())))
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
    """Runs a list of tasks asynchronously

    Given a particular limit, establish a semaphore and run up to limit tasks.
    Once the list of tasks is complete, return

    Args:
        limit (int): context object for retrieving configuration
        tasks (list): a list of tasks and checks
    """

    # TODO: return run task windows/info
    sem = asyncio.Semaphore(limit)

    async def sem_task(task):
        async with sem:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))
