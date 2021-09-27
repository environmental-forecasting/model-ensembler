import collections
import json
import logging
import os

import jsonschema

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

"""Configuration module

Contains classes, handlers and types relating to the configuration of ensembles
"""


path = os.path.abspath(os.path.dirname(__file__))


# TODO: Would like very much for some kind of itertools interactions to
#  generate parameter setups
class YAMLConfig:
    """Configuration processor for model-ensemble YAML-based configurations

    Args:
        configuration: Name of the YAML configuration to load
    """

    def __init__(self, configuration):
        self._schema = os.path.join(path, "model-ensemble.json")
        self._configuration_file = configuration

        self._schema_data, self._data = \
            self.__class__.validate(self._schema, self._configuration_file)

    @staticmethod
    def validate(json_schema, yaml_file):
        """Validate a YAML configuration against a JSON schema

        Args:
            json_schema (str): Name of schema to validate against
            yaml_file (str): Name of the configuration to validate

        Returns:
            tuple: contains JSON schema, YAML data
        """
        logging.debug("Assessing {} against {}".format(
            json_schema, yaml_file
        ))

        with open(yaml_file, "r") as fh:
            yaml_data = load(fh, Loader=Loader)

        # FIXME: this is a cheat for extreme batch numbers by allowing common
        #  parameters
        if "batch_config" in yaml_data["ensemble"]:
            batch_config = yaml_data["ensemble"]["batch_config"]

            for batch in yaml_data["ensemble"]["batches"]:
                for k, v in batch_config.items():
                    if k in ["name", "basedir"]:
                        raise RuntimeError("I can tell you now that putting "
                                           "those parameters in the general "
                                           "batch_config is a bad move")
                    if k not in batch:
                        batch[k] = v
            yaml_data["ensemble"].pop("batch_config", None)

        with open(json_schema, "r") as fh:
            json_data = json.load(fh)

        try:
            jsonschema.validate(instance=yaml_data, schema=json_data)
        except jsonschema.ValidationError as e:
            logging.error("There's an error with configuration file: {}".
                          format(yaml_file))
            raise e
        logging.info("Validated configuration file {} successfully".
                     format(yaml_file))
        return json_data, yaml_data


TaskSpec = collections.namedtuple('Task',
                                  ['name', 'args', 'value'])
TaskSpec.__new__.__defaults__ = (None, None)


class Task(TaskSpec):
    """Task definition class derived from the TaskSpec namedtuple"""
    pass


class TaskArrayMixin:
    """Generates sets of Task objects from Batch object members"""

    def task_array(self, attr):
        """Yields Tasks from a configuration instance

        Args:
            attr (str): Name of the member property in the configuration that
            defines the list of Task objects

        Yields:
            object: Task instance
        """
        field = getattr(self, attr)
        if field:
            for raw_task in field:
                yield Task(**raw_task)
        return None


# TODO: Make singleton
class EnsembleConfig(YAMLConfig, TaskArrayMixin):
    """Class to represent the entirety of the ensembler configuration

    Args:
        *args: See ``YAMLConfig``
        **kwargs: arbitrary keyword arguments
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vars = self._data['ensemble']['vars']
        self._pre_process = self._data['ensemble']['pre_process']
        self._post_process = self._data['ensemble']['post_process']
        self._batches = self._data['ensemble']['batches']

    @property
    def pre_process(self):
        """list(Task): preprocessing tasks"""
        return self.task_array("_pre_process")

    @property
    def post_process(self):
        """list(Task): postprocessing tasks"""
        return self.task_array("_post_process")

    @property
    def batches(self):
        """list(Batch): The batches contained in the ensemble configuration"""
        batches = list()
        for batch in self._batches:
            batches.append(Batch(**batch))
        return batches

    @property
    def vars(self):
        """dict: vars from ensemble configuration"""
        return self._vars


BatchSpec = collections.namedtuple("Batch",
                                   ["name", "templates", "templatedir",
                                    "job_file", "cluster", "basedir",
                                    "runs", "maxruns", "maxjobs",
                                    "email", "nodes", "ntasks", "length",
                                    "pre_batch", "pre_run", "post_run",
                                    "post_batch"])
BatchSpec.__new__.__defaults__ = (None, None, None, None,
                                  None, None, None, None)


class Batch(BatchSpec, TaskArrayMixin):
    """Class to represent the entirety of the ensembler configuration

    Args:
        pre_batch (object): TaskArray configuration setup
        pre_run (object): TaskArray configuration setup
        post_run (object): TaskArray configuration setup
        post_batch (object): TaskArray configuration setup
        **kwargs: Keyword arguments for BatchSpec instance
    """
    def __init__(self,
                 *args,
                 pre_batch=None, pre_run=None, post_run=None, post_batch=None,
                 **kwargs):
        super().__init__()
        self._pre_batch = pre_batch
        self._pre_run = pre_run
        self._post_run = post_run
        self._post_batch = post_batch

    @property
    def pre_batch(self):
        """list(Task): pre batch tasks"""
        return self.task_array("_pre_batch")

    @property
    def pre_run(self):
        """list(Task): pre run tasks"""
        return self.task_array("_pre_run")

    @property
    def post_run(self):
        """list(Task): post run tasks"""
        return self.task_array("_post_run")

    @property
    def post_batch(self):
        """list(Task): post batch tasks"""
        return self.task_array("_post_batch")
