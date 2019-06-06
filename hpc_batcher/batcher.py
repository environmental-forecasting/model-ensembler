import collections
import logging
import os
import shlex
import subprocess
import time

import hpc_batcher.tasks
from hpc_batcher.tasks import submit as slurm_submit
from hpc_batcher.tasks.utils import execute_command
from hpc_batcher.utils import Arguments

import jinja2

from pyslurm import config, job


# TODO: Split batches across threads, currently working on single batch
class Executor(object):
    def __init__(self, configuration):
        self._cfg = configuration
        self._args = Arguments()
        self.__active = None
        # TODO: Needs to be thread safe for multiple batches
        self.monitors = dict()
        # TODO: Preferable to monitor the above jobs and feed that into the system
        self._monitor_thread = None

    def run(self):
        logging.info("Running batcher")

        for batch in self._cfg.batches:
            self.__active = batch
            self.monitors[batch.name] = list()

            # TODO: The run should be object based, as it's dynamically updated based on flight checks
            for run in batch.runs:
                self.run_flight_tasks(run, "pre")

                # TODO: run object!
                run["runid"] = "{}-{}".format(self.active.name, batch.runs.index(run))
                run["rundir"] = os.path.join(self.active.basedir, run["runid"])

                # Submit the slurm run and monitor
                self.run_hpc_job(run)

                self.run_flight_tasks(run, "post")
            self.__active = None

    # TODO: Messy
    def run_hpc_job(self, run):
        cwd = os.getcwd()
        if not os.path.exists(self.active.basedir):
            raise ActiveBatchException("No basedir to process batch in!")
        os.chdir(self.active.basedir)

        rundir = run["rundir"]

        # Template out the slurm runner

        if os.path.exists(run["rundir"]):
            raise ActiveBatchException("Run directory {} already exists".format(rundir))

        os.mkdir(rundir, mode=0o775)
        # TODO: Hardcoded path

        sync = execute_command("rsync -rtgoD {}/ {}/".format(self.active.template_dir, rundir))
        if sync.returncode != 0:
            raise ActiveBatchException("Could not grab template directory {} to {}".format(
                self.active.template_dir, rundir
            ))

#        try:
        for tmpl_file in self.active.template:
            if tmpl_file[-3:] != ".j2":
                raise ActiveBatchException("{} doe not appear to be a Jinja2 template (.j2)".format(tmpl_file))

            tmpl_path = os.path.join(rundir, tmpl_file)
            with open(tmpl_path , "r") as fh:
                tmpl_data = fh.read()

            dst_file = tmpl_path[:-3]
            logging.info("Templating {} to {}".format(tmpl_path, dst_file))
            tmpl = jinja2.Template(tmpl_data)
            dst_data = tmpl.render(**run)
            with open(dst_file, "w+") as fh:
                fh.write(dst_data)

            os.unlink(tmpl_path)

        # hpc_batcher.tasks.hpc.submit()
        if self._args.nosubmission:
            logging.info("Skipping actual slurm submission based on arguments")
        else:
            job_id = slurm_submit(run, script=self.active.job_file)
            running = False

            # TODO: This will not catch jobs that have already finished!
            while not running:
                state = None
                try:
                    state = job().find_id(int(job_id))[0]['job_state']
                except ValueError:
                    logging.warning("Job {} not registered yet".format(job_id))

                if state and (state in ("RUNNING", "COMPLETED", "FAILED", "CANCELLED")):
                    running = True
                else:
                    # TODO: Configurable sleeps please!
                    time.sleep(2.)

            if job_id:
                self.monitors[self.active.name].append(job_id)
            else:
                raise ActiveBatchException("No job ID returned for submission")

        # TODO: Set up monitoring thread

    def run_flight_tasks(self, run, jobtype):
        result = False

        while not result:
            result = True

            for task in getattr(self.active, "{}flight_tasks".format(jobtype)):
                try:
                    func = getattr(hpc_batcher.tasks, task.name)
                    if not func(run, **task.args):
                        result = False
                        break
                except (PreflightException, PostflightException) as e:
                    logging.exception(e.message)

            if not result:
                logging.info("Cannot continue, waiting for next {}flight run".format(jobtype))
                time.sleep(10.)

    @property
    def active(self):
        if not self.__active:
            raise NoBatchException
        return self.__active

    @active.setter
    def active(self, b):
        if self.__active:
            raise ActiveBatchException
        self.__active = b


class PreflightException(Exception):
    pass


class PostflightException(Exception):
    pass


class NoBatchException(Exception):
    pass


class ActiveBatchException(Exception):
    pass

