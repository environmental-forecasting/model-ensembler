import pytest
import asyncio
import warnings
from unittest.mock import MagicMock, patch

import model_ensembler.batcher as batcher

class DummyRun:
    def __init__(self, id):
        self.id = id

class DummyBatch:
    def __init__(self):
        self.name = "testbatch"
        self.maxjobs = 1
        self.maxruns = 1
        self.basedir = "/tmp"
        self.templates = []
        self.pre_run = []
        self.post_run = []
        self.pre_batch = []
        self.post_batch = []
        self.runs = [dict()]
        self.job_file = "job.sh"
        self.repeat = False
    def _asdict(self):
        return {
            "name": self.name,
            "maxjobs": self.maxjobs,
            "maxruns": self.maxruns,
            "basedir": self.basedir,
            "templates": self.templates,
            "pre_run": self.pre_run,
            "post_run": self.post_run,
            "pre_batch": self.pre_batch,
            "post_batch": self.post_batch,
            "runs": self.runs,
            "job_file": self.job_file,
            "repeat": self.repeat,
        }

class DummyCluster:
    START_STATES = {"RUNNING"}
    FINISH_STATES = {"COMPLETED"}
    def __init__(self):
        self.state = "COMPLETED"
    async def submit_job(self, run, script=None):
        return 123
    async def find_id(self, job_id):
        class Job:
            state = "COMPLETED"
        return Job()

@pytest.mark.asyncio
async def test_run_batch_item_success(monkeypatch):
    """
    Test that run_batch_item returns correct job_id and run object on success.
    Mocks all dependencies to simulate a successful batch run.
    """
    batch = DummyBatch()
    run = DummyRun(id="run1")
    batcher.batch_ctx.set(batch)
    batcher.cluster_ctx.set(DummyCluster())
    async def dummy_prepare_run_directory(b, r):
        return None
    monkeypatch.setattr(batcher, "prepare_run_directory", dummy_prepare_run_directory)
    monkeypatch.setattr(batcher, "process_templates", lambda r, t: None)
    async def dummy_run_task_items(x):
        return None
    monkeypatch.setattr(batcher, "run_task_items", dummy_run_task_items)
    async def dummy_run_check(f, c):
        return None
    monkeypatch.setattr(batcher, "run_check", dummy_run_check)
    class DummyArguments:
        no_submission = False
    monkeypatch.setattr(batcher, "Arguments", lambda: DummyArguments)
    batcher._batch_job_sems[batch.name] = asyncio.Semaphore(1)
    job_id, result_run = await batcher.run_batch_item(run)
    assert job_id == 123
    assert result_run == run

@pytest.mark.asyncio
async def test_run_batch_item_templating_error(monkeypatch):
    """
    Test that run_batch_item returns None and run object when templating fails.
    Simulates a TemplatingError during job preparation.
    """
    batch = DummyBatch()
    run = DummyRun(id="run2")
    batcher.batch_ctx.set(batch)
    batcher.cluster_ctx.set(DummyCluster())
    class DummyTemplatingError(Exception):
        pass
    monkeypatch.setattr(batcher, "prepare_run_directory", lambda b, r: (_ for _ in ()).throw(batcher.TemplatingError("fail")))
    monkeypatch.setattr(batcher, "process_templates", lambda r, t: None)
    async def dummy_run_task_items(x):
        return None
    monkeypatch.setattr(batcher, "run_task_items", dummy_run_task_items)
    job_id, result_run = await batcher.run_batch_item(run)
    assert job_id is None
    assert result_run == run


def test_batch_executor_init(monkeypatch):
    """
    Test BatchExecutor initialization and context setup.
    Ensures that the configuration is stored and context is initialized.
    """
    class DummyCfg:
        vars = {"foo": "bar"}
        pre_process = []
        post_process = []
        batches = [DummyBatch()]
    monkeypatch.setattr(batcher, "init_hpc_backend", lambda nom: None)
    monkeypatch.setattr(batcher.importlib, "import_module", lambda nom: DummyCluster)
    be = batcher.BatchExecutor(DummyCfg(), backend="dummy", extra_vars=["x"])
    assert be._cfg.vars["foo"] == "bar"



def test_do_batch_execution(monkeypatch, tmp_path):
    """
    Test do_batch_execution for a batch with two runs.
    Mocks all async dependencies and context variables, ensures all coroutines are awaited.
    Checks that the batch execution returns 'Success'.
    """
    batch = DummyBatch()
    batch.basedir = str(tmp_path)
    batch.runs = [dict(), dict()]
    batch.name = "batchtest"
    batch.maxjobs = 1
    batch.maxruns = 2
    batcher.batch_ctx.set(batch)
    batcher.run_ctx.set({})
    batcher.extra_ctx.set({})

    async def dummy_run_task_items(x):
        return None
    monkeypatch.setattr(batcher, "run_task_items", dummy_run_task_items)

    class DummyRunWithIdx:
        def __init__(self, id, idx):
            self.id = id
            self.idx = idx

    async def dummy_run_batch_item(run):
        return 123, DummyRunWithIdx(run.id, run.idx)
    monkeypatch.setattr(batcher, "run_batch_item", dummy_run_batch_item)

    async def dummy_run_runner(maxruns, tasks):
        # Await all tasks to avoid RuntimeWarning
        results = []
        for coro in tasks:
            results.append(await coro)
        return results
    monkeypatch.setattr(batcher, "run_runner", dummy_run_runner)

    class DummyArguments:
        indexes = []
        skips = 0
    monkeypatch.setattr(batcher, "Arguments", lambda: DummyArguments)

    loop = asyncio.new_event_loop()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        result = batcher.do_batch_execution(loop, batch)
    assert result == "Success"
