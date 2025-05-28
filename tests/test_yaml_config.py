import pytest
import os

from model_ensembler.config import YAMLConfig

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../examples")
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "../model_ensembler/model-ensemble.json"
)

@pytest.mark.parametrize("yaml_file", [
    "sanity-check.yml"
])

def test_example_yaml_config_valid(yaml_file):
    config_path = os.path.join(EXAMPLES_DIR, yaml_file)

    class TestYAMLConfig(YAMLConfig):
        def __init__(self, configuration):
            self._schema = SCHEMA_PATH
            self._configuration_file = configuration
            self._schema_data, self._data = self.__class__.validate(self._schema, self._configuration_file)
        
    config = TestYAMLConfig(config_path)

    assert isinstance(config._data, dict)
    assert "ensemble" in config._data
