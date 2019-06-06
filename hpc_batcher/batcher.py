import logging
import os
import threading
import time

import hpc_batcher.tasks
from hpc_batcher.tasks import submit as slurm_submit
from hpc_batcher.tasks.utils import execute_command
from hpc_batcher.utils import Arguments

import jinja2

from pyslurm import config, job


# TODO: Need to implement locking, currently the run thread should be safe
class Run(object):
    def __init__(self, batch, runid, rundir, runargs=None):
        self.runid = runid
        self.dir = rundir

        self.slurm_id = None
        self.slurm_running = False
        self.slurm_state = None
        self.slurm_ready = False

        batch_dict = batch._asdict()
        for k, v in batch_dict.items():
            if not k.endswith("_tasks") and k != "runs" and k != "name":
                setattr(self, "{}".format(k), v)

        if runargs:
            self.__dict__.update(runargs)

        self.running = False
        self.batch = batch

        self._thread = threading.Thread(name=runid, target=self.run)

    def run(self):
        logging.info("Starting ")
        if not self.run_tasks(self.batch.preprocess_tasks):
            raise ProcessingException("Run preprocessing failed")

        while not self.slurm_ready:
            logging.info("HPC not ready for {}".format(self.runid))
            time.sleep(10.)

        if Arguments().nosubmission:
            logging.info("Skipping actual slurm submission based on arguments")
            self.slurm_id = self.name
        else:
            self.slurm_id = slurm_submit(self, script=self.batch.job_file)

            while not self.slurm_running:
                try:
                    self.slurm_state = job().find_id(int(self.slurm_id))[0]['job_state']
                except ValueError:
                    logging.warning("Job {} not registered yet".format(self.slurm_id))

                if self.slurm_state and (self.slurm_state in ("RUNNING", "COMPLETED", "FAILED", "CANCELLED")):
                    self.slurm_running = True
                else:
                    # TODO: Configurable sleeps please!
                    time.sleep(2.)

            while self.running:
                self.slurm_state = job().find_id(int(self.slurm_id))[0]['job_state']
                logging.info("{} monitor got state {} for job {}".format(
                    self.runid, self.slurm_state, self.slurm_id))

                if self.slurm_state in ("COMPLETED", "FAILED", "CANCELLED"):
                    break
                else:
                    time.sleep(10.)

        ret = self.run_tasks(self.batch.postprocess_tasks)
        self.running = False
        if not ret:
            raise ProcessingException("Run postprocessing failure")

    def submit(self):
        self.running = True
        self._thread.start()

    def run_tasks(self, tasks):
        for task in tasks:
            try:
                func = getattr(hpc_batcher.tasks, task.name)
                func(self, **task.args)
            except ProcessingException as e:
                logging.exception(e)
                return False
        return True


# TODO: Work on multi-batches
class Executor(object):
    def __init__(self, configuration):
        self._cfg = configuration
        self._args = Arguments()
        self.__active = None
        # TODO: Needs to be thread safe for multiple batches
        self.runs = dict()

    def run(self):
        logging.info("Running batcher")

        for batch in self._cfg.batches:
            self.__active = batch
            self.runs[batch.name] = list()

            for run in batch.runs:
                runid = "{}-{}".format(self.active.name, batch.runs.index(run))
                self.runs[batch.name].append(Run(batch=batch,
                                             runid=runid,
                                             rundir=os.path.join(self.active.basedir, runid),
                                             runargs=run))

            for run in self.runs[batch.name]:
                self.prep_hpc_job(run)

                self.run_flight_tasks(run, "pre")
                run.submit()

                active = len([r for r in self.runs[batch.name] if r.running])
                while active >= batch.maxruns:
                    logging.info("Waiting for number of running threads to diminish {} ({})".format(
                        active, batch.maxruns))
                    time.sleep(10.)
                    active = len([r for r in self.runs[batch.name] if r.running])

                run.slurm_ready = True

                self.run_flight_tasks(run, "post")
            self.__active = None

    # TODO: Messy
    def prep_hpc_job(self, run):
        if not os.path.exists(self.active.basedir):
            raise ActiveBatchException("No basedir to process batch in!")
        os.chdir(self.active.basedir)

        # Template out the slurm runner

        if os.path.exists(run.dir):
            raise ActiveBatchException("Run directory {} already exists".format(run.dir))

        os.mkdir(run.dir, mode=0o775)
        # TODO: Hardcoded path

        sync = execute_command("rsync -aXE {}/ {}/".format(self.active.template_dir, run.dir))
        if sync.returncode != 0:
            raise ActiveBatchException("Could not grab template directory {} to {}".format(
                self.active.template_dir, run.dir
            ))

        for tmpl_file in self.active.template:
            if tmpl_file[-3:] != ".j2":
                raise ActiveBatchException("{} doe not appear to be a Jinja2 template (.j2)".format(tmpl_file))

            tmpl_path = os.path.join(run.dir, tmpl_file)
            with open(tmpl_path , "r") as fh:
                tmpl_data = fh.read()

            dst_file = tmpl_path[:-3]
            logging.info("Templating {} to {}".format(tmpl_path, dst_file))
            tmpl = jinja2.Template(tmpl_data)
            dst_data = tmpl.render(run=vars(run))
            with open(dst_file, "w+") as fh:
                fh.write(dst_data)
            os.chmod(dst_file, os.stat(tmpl_path).st_mode)

            os.unlink(tmpl_path)

    # TODO: LOCK during this phase to avoid conflicts
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
                except RuntimeError as e:
                    msg = "Issues with flight checks, abandoning"
                    logging.exception(e)
                    raise FlightException("Issues with flight checks, abandoning")

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


class FlightException(Exception):
    pass


class ProcessingException(Exception):
    pass


class NoBatchException(Exception):
    pass


class ActiveBatchException(Exception):
    pass

