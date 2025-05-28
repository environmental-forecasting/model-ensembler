import os
import glob
import pytest

from model_ensembler.config import YAMLConfig

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../examples")
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "../model_ensembler/model-ensemble.json"
)

def list_yaml_files():
    return glob.glob(os.path.join(EXAMPLES_DIR, "*y*ml"))


@pytest.mark.parametrize("yaml_file", list_yaml_files())

def test_example_yamls_config_valid(yaml_file):
    """
    Validate all YAML configs in examples/ folder conform to schema
    """
    config_path = os.path.join(EXAMPLES_DIR, yaml_file)

    class TestYAMLConfig(YAMLConfig):
        def __init__(self, configuration):
            self._schema = SCHEMA_PATH
            self._configuration_file = configuration
            self._schema_data, self._data = self.__class__.validate(self._schema, self._configuration_file)

    config = TestYAMLConfig(yaml_file)

    assert isinstance(config._data, dict)
    assert "ensemble" in config._data
