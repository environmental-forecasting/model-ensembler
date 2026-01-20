import pytest
import asyncio
import importlib

import model_ensembler.batcher as batcher
import model_ensembler.runners as runners
import model_ensembler.tasks as tasks
import model_ensembler.utils as utils


class DummyArgs:
    def __init__(self, check_timeout=0.01):
        self.check_timeout = check_timeout


class DummyCheck:
    check = True
    def __init__(self, succeed_after=0, raise_exc=False):
        self.calls = 0
        self.succeed_after = succeed_after
        self.raise_exc = raise_exc
    
    async def __call__(self, ctx, **kwargs):
        self.calls += 1
        if self.raise_exc:
            raise Exception("fail")
        return self.calls > self.succeed_after


class DummyTask:
    check = False
    def __init__(self, raise_exc=False):
        self.called = False
        self.raise_exc = raise_exc
    
    async def __call__(self, ctx, **kwargs):
        self.called = True
        if self.raise_exc:
            raise Exception("fail")
        return True


class DummyItem:
    def __init__(self, name, func):
        self.name = name
        self.args = {}
        self.func = func


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment with dummy args and run context."""
    args = DummyArgs()
    monkeypatch.setattr(runners, "Arguments", lambda: args)
    utils.Arguments.instance = args
    batcher.run_ctx.set({})


def make_check_config(**args):
    """Create a check configuration object."""
    return type("Check", (), {"args": args})()


def make_task_config(**args):
    """Create a task configuration object.""" 
    return type("Task", (), {"args": args})()

def test_run_check_success():
    """Test check that succeeds immediately."""
    check_func = DummyCheck(succeed_after=0)
    check = make_check_config()
    
    asyncio.run(runners.run_check(check_func, check))
    assert check_func.calls == 1


def test_run_check_retry():
    """Test check that retries before succeeding."""
    check_func = DummyCheck(succeed_after=2)
    check = make_check_config()
    
    asyncio.run(runners.run_check(check_func, check))
    assert check_func.calls == 3


def test_run_check_exception():
    """Test check that raises an exception."""
    check_func = DummyCheck(raise_exc=True)
    check = make_check_config()
    
    with pytest.raises(runners.CheckException):
        asyncio.run(runners.run_check(check_func, check))


def test_run_task_success():
    """Test successful task execution."""
    task_func = DummyTask()
    task = make_task_config()
    
    result = asyncio.run(runners.run_task(task_func, task))
    assert result is True
    assert task_func.called


def test_run_task_exception():
    """Test task that raises an exception."""
    task_func = DummyTask(raise_exc=True)
    task = make_task_config()
    
    with pytest.raises(runners.TaskException):
        asyncio.run(runners.run_task(task_func, task))

def test_run_task_items_success(monkeypatch):
    """Test successful execution of mixed check and task items."""
    dummy_check = DummyCheck(succeed_after=0)
    dummy_task = DummyTask()
    
    monkeypatch.setattr(tasks, "check_func", dummy_check, raising=False)
    monkeypatch.setattr(tasks, "task_func", dummy_task, raising=False)
    
    items = [
        DummyItem("check_func", dummy_check), 
        DummyItem("task_func", dummy_task)
    ]
    
    asyncio.run(runners.run_task_items(items))
    assert dummy_check.calls == 1
    assert dummy_task.called


def test_run_task_items_exception(monkeypatch):
    """Test task items execution with exception handling."""
    dummy_check = DummyCheck(raise_exc=True)
    
    monkeypatch.setattr(tasks, "check_func", dummy_check, raising=False)
    items = [DummyItem("check_func", dummy_check)]
    
    with pytest.raises(runners.ProcessingException):
        asyncio.run(runners.run_task_items(items))


def test_run_runner():
    """Test concurrent task execution with semaphore limit."""
    async def dummy_task(n):
        await asyncio.sleep(0.01)
        return n
    
    tasks = [dummy_task(i) for i in range(5)]
    results = asyncio.run(runners.run_runner(2, tasks))
    assert sorted(results) == [0, 1, 2, 3, 4]
