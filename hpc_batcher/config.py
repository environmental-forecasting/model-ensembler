import collections
import json
import jsonschema
import logging
import os

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

path = os.path.abspath(os.path.dirname(__file__))


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


# TODO: Make singleton
class BatcherConfig(YAMLConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._batches = self._data['hpc_batcher']['batches']

    @property
    def batches(self):
        return [Batch(**b) for b in self._batches]


# TODO: Derive the fields from the schema
BatchSpec = collections.namedtuple('Batch',
                                   ['name', 'template', 'template_dir', 'job_file', 'cluster', 'basedir',
                                    "runs", "maxruns",
                                    "email", "nodes", "ntasks", "days",
                                    'preflight', "preprocess", "postprocess", "postflight"])
BatchSpec.__new__.__defaults__ = tuple([None for i in range(0, 8)])


class Batch(BatchSpec):

    def task_array(self, type):
        field = getattr(self, type)
        if field:
            for raw_task in field:
                yield Task(**raw_task)
        return None

    @property
    def preprocess_tasks(self):
        return self.task_array("preprocess")

    @property
    def postprocess_tasks(self):
        return self.task_array("postprocess")

    @property
    def preflight_tasks(self):
        return self.task_array("preflight")

    @property
    def postflight_tasks(self):
        return self.task_array("postflight")



TaskSpec = collections.namedtuple('Task',
                                  ['name', 'args', 'value'])
TaskSpec.__new__.__defaults__ = (None, None)


class Task(TaskSpec):
    pass


