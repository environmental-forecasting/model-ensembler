import os
import pytest
import asyncio
import logging

import model_ensembler.templates as templates
import model_ensembler.utils as utils
from model_ensembler.exceptions import TemplatingError


class DummyBatch:
    def __init__(self):
        self.templatedir = "/tmp/templates"
        self.templates = ["file1.j2", "file2.j2"]


class DummyRun:
    def __init__(self):
        self.id = "run1"
        self.dir = "/tmp/run1"


class DummyArgs:
    def __init__(self, pickup=False):
        self.pickup = pickup


@pytest.fixture
def dummy_batch():
    return DummyBatch()


@pytest.fixture
def dummy_run():
    return DummyRun()


def setup_args_patch(monkeypatch, pickup=False):
    """Setup Arguments for tests."""
    args = DummyArgs(pickup=pickup)
    monkeypatch.setattr(templates, "Arguments", lambda: args)
    utils.Arguments.instance = args


def setup_subprocess_mock(monkeypatch, return_code=0):
    """Setup asyncio subprocess mocking."""
    async def dummy_subprocess_exec(*a, **kw):
        class DummyProc:
            async def wait(self):
                return return_code
        return DummyProc()
    monkeypatch.setattr("asyncio.create_subprocess_exec", dummy_subprocess_exec)

@pytest.mark.asyncio
async def test_prepare_run_directory_creates_dir(monkeypatch, dummy_batch, dummy_run):
    """Test successful directory creation and rsync."""
    monkeypatch.setattr("os.path.exists", lambda path: False)
    monkeypatch.setattr("os.makedirs", lambda path, mode=0o775: None)
    monkeypatch.setattr("shlex.split", lambda cmd: cmd.split())
    setup_args_patch(monkeypatch, pickup=False)
    setup_subprocess_mock(monkeypatch, return_code=0)
    
    await templates.prepare_run_directory(dummy_batch, dummy_run)


@pytest.mark.asyncio
async def test_prepare_run_directory_pickup(monkeypatch, dummy_batch, dummy_run):
    """Test pickup mode - copying templates to existing directory."""
    monkeypatch.setattr("os.path.exists", lambda path: True)
    monkeypatch.setattr("shutil.copy", lambda src, dst: dst)
    setup_args_patch(monkeypatch, pickup=True)
    
    logs = []
    monkeypatch.setattr(logging, "info", lambda msg, *a: logs.append(msg))
    
    await templates.prepare_run_directory(dummy_batch, dummy_run)
    assert any("Picked up previous job directory" in l for l in logs)


@pytest.mark.asyncio
async def test_prepare_run_directory_dir_exists_error(monkeypatch, dummy_batch, dummy_run):
    """Test error when directory exists and not in pickup mode."""
    monkeypatch.setattr("os.path.exists", lambda path: True)
    setup_args_patch(monkeypatch, pickup=False)
    
    with pytest.raises(TemplatingError):
        await templates.prepare_run_directory(dummy_batch, dummy_run)


@pytest.mark.asyncio
async def test_prepare_run_directory_rsync_error(monkeypatch, dummy_batch, dummy_run):
    """Test error when rsync fails."""
    monkeypatch.setattr("os.path.exists", lambda path: False)
    monkeypatch.setattr("os.makedirs", lambda path, mode=0o775: None)
    monkeypatch.setattr("shlex.split", lambda cmd: cmd.split())
    setup_args_patch(monkeypatch, pickup=False)
    setup_subprocess_mock(monkeypatch, return_code=1)
    
    with pytest.raises(TemplatingError):
        await templates.prepare_run_directory(dummy_batch, dummy_run)


def test_process_templates_success(monkeypatch, tmp_path):
    """Test successful template processing."""
    run = DummyRun()
    run.dir = str(tmp_path)
    tmpl_file = "test.j2"
    template_path = os.path.join(run.dir, tmpl_file)
    
    with open(template_path, "w") as f:
        f.write("Hello {{ run.id }}!")
    
    monkeypatch.setattr("os.chmod", lambda f, m: None)
    monkeypatch.setattr("os.unlink", lambda f: None)
    logs = []
    monkeypatch.setattr(logging, "info", lambda msg, *a: logs.append(msg))
    
    templates.process_templates(run, [tmpl_file])
    
    dst_file = os.path.join(run.dir, "test")
    assert os.path.exists(dst_file)
    with open(dst_file) as f:
        assert "Hello run1!" in f.read()
    assert any("Templating" in l for l in logs)


def test_process_templates_non_j2(tmp_path):
    """Test error for non-.j2 files."""
    run = DummyRun()
    run.dir = str(tmp_path)
    tmpl_file = "test.txt"
    
    with open(os.path.join(run.dir, tmpl_file), "w") as f:
        f.write("data")
    
    with pytest.raises(TemplatingError, match="does not appear to be a Jinja2 template"):
        templates.process_templates(run, [tmpl_file])


def test_process_templates_oserror(monkeypatch):
    """Test error handling for file operations."""
    run = DummyRun()
    tmpl_file = "test.j2"
    
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(OSError()))
    
    with pytest.raises(TemplatingError, match="Could not template"):
        templates.process_templates(run, [tmpl_file])
