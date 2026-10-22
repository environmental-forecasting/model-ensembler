import shutil
import subprocess
import sys
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_dummy_backend_ensemble_runs_end_to_end(tmp_path):
    """Run a full ensemble on the dummy backend in a fresh interpreter.

    A fresh process is used so no event loop is pre-set by pytest, which is
    what the CLI sees in real use. In-process tests of the batcher bypass
    BatchExecutor.run() and so miss event loop handling that differs between
    Python versions (e.g. asyncio.get_event_loop() raising on 3.14).
    """
    workdir = tmp_path / "examples"
    shutil.copytree(EXAMPLES, workdir)
    # The example scripts sleep for random periods; drop that to keep the test fast
    for template in (workdir / "template_job").glob("*.j2"):
        lines = template.read_text().splitlines(keepends=True)
        template.write_text("".join(
            "SLEEP_SECS=0\n" if line.startswith("SLEEP_SECS=") else line
            for line in lines))
    for batch in ("tst1", "tst2"):
        (workdir / batch).mkdir()
        (workdir / batch / "batch.ready").touch()

    result = subprocess.run(
        [sys.executable, "-c",
         "from model_ensembler.cli import main; main()",
         "test.yaml", "dummy",
         "-ct", "1", "-st", "1", "-rt", "1", "-et", "1", "-ms", "1"],
        cwd=workdir, capture_output=True, text=True, timeout=300)

    assert result.returncode == 0, result.stdout + result.stderr
    for batch in ("tst1", "tst2"):
        assert (workdir / batch / "pre_batch.keep").exists()
        assert (workdir / batch / "post_batch.keep").exists()
        run_dirs = list((workdir / batch).glob(batch + "-*"))
        assert len(run_dirs) == 4
        for run_dir in run_dirs:
            assert (run_dir / "pre_run.keep").exists()
            assert (run_dir / "post_run.keep").exists()
