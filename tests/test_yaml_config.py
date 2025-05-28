import os
import glob
import pytest
import jsonschema
from model_ensembler.config import YAMLConfig

BASE_DIR = os.path.dirname(__file__)
EXAMPLES_DIR = os.path.join(BASE_DIR, "../examples")
INVALID_DIR = os.path.join(BASE_DIR, "../examples/invalid_yamls")
SCHEMA_PATH = os.path.join(BASE_DIR, "../model_ensembler/model-ensemble.json")


class TestYAMLConfig:
    @staticmethod
    def list_yaml_files():
        return glob.glob(os.path.join(EXAMPLES_DIR, "*y*ml"))

    class YAMLConfigWrapper(YAMLConfig):
        def __init__(self, configuration):
            self._schema = SCHEMA_PATH
            self._configuration_file = configuration
            self._schema_data, self._data = self.__class__.validate(
                self._schema, self._configuration_file
            )

    @pytest.mark.parametrize("yaml_file", list_yaml_files.__func__())
    def test_example_yamls_config_valid(self, yaml_file):
        """
        Validate all YAML configs in examples/ folder conform to schema
        """
        config = self.YAMLConfigWrapper(yaml_file)

        assert isinstance(config._data, dict)
        assert "ensemble" in config._data

    @pytest.mark.parametrize(
        "filename,expected_error",
        {
            "missing_name.yaml": "is a required property",
            "bad_type.yaml": "is not of type",
            "invalid_batch_config.yaml": "'name' and 'basedir' should be defined",
        }.items(),
    )
    def test_example_yamls_config_invalid(self, filename, expected_error):
        """
        Validate that YAML configs in invalid_yamls/ folder throw expected error
        """
        yaml_path = os.path.join(INVALID_DIR, filename)

        with pytest.raises((jsonschema.ValidationError, RuntimeError)) as exc_info:
            self.YAMLConfigWrapper(yaml_path)

        assert expected_error in str(
            exc_info.value
        ), f"Expected '{expected_error}' in error for {filename}"
