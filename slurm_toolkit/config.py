import collections
import json
import jsonschema
import logging
import os

from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

path = os.path.abspath(os.path.dirname(__file__))


# TODO: Would like very much for some kind of itertools interactions to generate parameter setups
class YAMLConfig(object):
    def __init__(self, configuration):
        self._schema = os.path.join(path, "config-schema.json")
        self._configuration_file = configuration

        self._schema_data, self._data = \
            self.__class__.validate(self._schema, self._configuration_file)

    @staticmethod
    def validate(json_schema, yaml_file):
        logging.debug("Assessing {} against {}".format(
            json_schema, yaml_file
        ))

        with open(yaml_file, "r") as fh:
            yaml_data = load(fh, Loader=Loader)

        with open(json_schema, "r") as fh:
            json_data = json.load(fh)

        try:
            jsonschema.validate(instance=yaml_data, schema=json_data)
        except jsonschema.ValidationError as e:
            logging.error("There's an error with configuration file: {}".format(yaml_file))
            raise e
        logging.info("Validated configuration file {} successfully".format(yaml_file))
        return json_data, yaml_data


TaskSpec = collections.namedtuple('Task',
                                  ['name', 'args', 'value'])
TaskSpec.__new__.__defaults__ = (None, None)


class Task(TaskSpec):
    pass


class TaskArrayMixin:
    def task_array(self, attr):
        field = getattr(self, attr)
        if field:
            for raw_task in field:
                yield Task(**raw_task)
        return None


# TODO: Make singleton
class BatcherConfig(YAMLConfig, TaskArrayMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vars = self._data['slurm_toolkit']['vars']
        self._pre_process = self._data['slurm_toolkit']['pre_process']
        self._post_process = self._data['slurm_toolkit']['post_process']
        self._batches = self._data['slurm_toolkit']['batches']

    @property
    def pre_process(self):
        return self.task_array("_pre_process")

    @property
    def post_process(self):
        return self.task_array("_post_process")

    @property
    def batches(self):
        batches = list()
        for b in self._batches:
            batches.append(Batch(**b))
        return batches

    @property
    def vars(self):
        return self._vars


BatchSpec = collections.namedtuple("Batch",
                                   ["name", "templates", "templatedir", "job_file", "cluster", "basedir",
                                    "runs", "maxruns",
                                    "email", "nodes", "ntasks", "days",
                                    "pre_batch", "pre_run", "post_run", "post_batch"])
BatchSpec.__new__.__defaults__ = tuple([None for i in range(0, 8)])


class Batch(BatchSpec, TaskArrayMixin):
    def __init__(self, *args, pre_batch=None, pre_run=None, post_run=None, post_batch=None, **kwargs):
        super().__init__()
        self._pre_batch = pre_batch
        self._pre_run = pre_run
        self._post_run = post_run
        self._post_batch = post_batch

    @property
    def pre_batch(self):
        return self.task_array("_pre_batch")

    @property
    def pre_run(self):
        return self.task_array("_pre_run")

    @property
    def post_run(self):
        return self.task_array("_post_run")

    @property
    def post_batch(self):
        return self.task_array("_post_batch")

