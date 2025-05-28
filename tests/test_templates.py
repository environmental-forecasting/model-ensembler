import pytest

import unittest.mock as mock

from model_ensembler.templates import prepare_run_directory


# Need to create mock batch and runs
@pytest.fixture
def batch():
    return mock.Mock(
        templatedir="examples/template_job",
        templates=["inputfile.j2", "pre_run.sh.j2"]
    )


@pytest.fixture
def run():
    return mock.Mock(
        dir="/run/dir",
        id="run1"
    )


async def test_pickup_mode_true(batch, run):
    with mock.patch('model_ensembler.templates.Arguments', return_value=mock.Mock(pickup=True)), \
         mock.patch('os.path.exists', return_value=True), \
         mock.patch('shutil.copy', side_effect=lambda src, dst: dst), \
         mock.patch('logging.info') as log_mock:

        await prepare_run_directory(batch, run)

        assert log_mock.call_count >= 1