import os
import pytest
import tempfile
import yaml
import json
import jsonschema
from model_ensembler.config import YAMLConfig, EnsembleConfig, Batch, Task

# Schema path for validation testing
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../model_ensembler/model-ensemble.json")

# Embedded example configurations for unit tests
VALID_CONFIG_DATA = {
    "minimal": {
        "ensemble": {
            "batches": [{
                "name": "batch1", 
                "basedir": "/tmp",
                "templates": ["test.j2"],
                "templatedir": "/tmp/templates",
                "runs": [],
                "maxruns": 1,
                "maxjobs": 1
            }],
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    },
    "with_tasks": {
        "ensemble": {
            "batches": [{
                "name": "batch1", 
                "basedir": "/tmp",
                "templates": ["test.j2"],
                "templatedir": "/tmp/templates",
                "runs": [{"param": "value"}],
                "maxruns": 2,
                "maxjobs": 1,
                "pre_run": [{"name": "setup"}],
                "post_run": [{"name": "cleanup"}]
            }],
            "vars": {"key": "value"},
            "pre_process": [{"name": "global_setup"}],
            "post_process": [{"name": "global_cleanup"}]
        }
    },
    "with_batch_config": {
        "ensemble": {
            "batches": [{
                "name": "batch1", 
                "basedir": "/tmp",
                "templates": ["test.j2"],
                "templatedir": "/tmp/templates", 
                "runs": [],
                "maxruns": 1,
                "maxjobs": 1
            }],
            "batch_config": {"nodes": 2},
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    }
}

INVALID_CONFIG_DATA = {
    "missing_batches": {
        "ensemble": {
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    },
    "invalid_batch_config": {
        "ensemble": {
            "batches": [{"basedir": "/tmp"}],
            "batch_config": {"name": "bad", "basedir": "/bad"},
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    },
    "missing_required_fields": {
        "ensemble": {
            "batches": [{"name": "batch1"}],  # Missing required fields
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    },
    "bad_type": {
        "ensemble": {
            "batches": "not_a_list",  # Should be a list
            "vars": {},
            "pre_process": [],
            "post_process": []
        }
    }
}


class TestYAMLConfig:
    @staticmethod
    def create_temp_yaml(data):
        """Create a temporary YAML file with given data."""
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w") as f:
            yaml.dump(data, f)
        return path

    class YAMLConfigWrapper(YAMLConfig):
        """Wrapper class to override schema path for testing."""
        def __init__(self, configuration):
            self._schema = SCHEMA_PATH
            self._configuration_file = configuration
            self._schema_data, self._data = self.__class__.validate(
                self._schema, self._configuration_file
            )

    @pytest.mark.parametrize("config_name,config_data", VALID_CONFIG_DATA.items())
    def test_valid_config_validation(self, config_name, config_data):
        """Test validation of various valid configuration structures."""
        yaml_path = self.create_temp_yaml(config_data)
        try:
            config = self.YAMLConfigWrapper(yaml_path)
            assert isinstance(config._data, dict), f"Config data should be dict for {config_name}"
            assert "ensemble" in config._data, f"Missing 'ensemble' key in {config_name}"
            assert isinstance(config._schema_data, dict), f"Schema data should be dict for {config_name}"
            
            # Verify essential structure
            ensemble = config._data["ensemble"]
            assert "batches" in ensemble, f"Missing 'batches' in ensemble for {config_name}"
            assert isinstance(ensemble["batches"], list), f"Batches should be list for {config_name}"
            assert len(ensemble["batches"]) > 0, f"Batches should not be empty for {config_name}"
        finally:
            os.unlink(yaml_path)

    @pytest.mark.parametrize("config_name,config_data", INVALID_CONFIG_DATA.items())
    def test_invalid_config_validation(self, config_name, config_data):
        """Test validation of invalid configuration structures."""
        yaml_path = self.create_temp_yaml(config_data)
        try:
            with pytest.raises((jsonschema.ValidationError, RuntimeError), 
                             match=f".*") as exc_info:
                self.YAMLConfigWrapper(yaml_path)
            assert exc_info.value is not None, f"Expected validation error for {config_name}"
        finally:
            os.unlink(yaml_path)

    @pytest.mark.parametrize(
        "config_name,expected_error",
        [
            ("missing_required_fields", "is a required property"),
            ("bad_type", "is not of type"),
            ("invalid_batch_config", "'name' and 'basedir' should be defined"),
        ],
    )
    def test_invalid_specific_errors(self, config_name, expected_error):
        """Test validation of specific invalid configuration scenarios."""
        config_data = INVALID_CONFIG_DATA[config_name]
        yaml_path = self.create_temp_yaml(config_data)
        try:
            with pytest.raises((jsonschema.ValidationError, RuntimeError)) as exc_info:
                self.YAMLConfigWrapper(yaml_path)

            assert expected_error in str(exc_info.value), (
                f"Expected '{expected_error}' in error for {config_name}, "
                f"but got: {exc_info.value}"
            )
        finally:
            os.unlink(yaml_path)

    def test_ensemble_config_instantiation(self):
        """Test that EnsembleConfig can be instantiated with valid configurations."""
        yaml_path = self.create_temp_yaml(VALID_CONFIG_DATA["with_tasks"])
        try:
            config = EnsembleConfig(yaml_path)
            assert hasattr(config, 'vars')
            assert hasattr(config, 'batches')
            assert hasattr(config, 'pre_process')
            assert hasattr(config, 'post_process')
            
            # Test property access
            assert config.vars == {"key": "value"}
            batches = config.batches
            assert len(batches) == 1
            assert batches[0].name == "batch1"
        finally:
            os.unlink(yaml_path)

    def test_batch_config_properties(self):
        """Test Batch configuration properties and task arrays."""
        # Test with minimal batch config
        batch = Batch(
            name="test_batch",
            basedir="/tmp",
            pre_batch=[{"name": "task1", "args": {"key": "value"}}],
            post_run=[{"name": "task2"}]
        )
        
        assert batch.name == "test_batch"
        assert batch.basedir == "/tmp"
        
        # Test task arrays
        pre_batch_tasks = list(batch.pre_batch)
        assert len(pre_batch_tasks) == 1
        assert pre_batch_tasks[0].name == "task1"
        assert pre_batch_tasks[0].args == {"key": "value"}
        
        post_run_tasks = list(batch.post_run)
        assert len(post_run_tasks) == 1
        assert post_run_tasks[0].name == "task2"

    def test_task_creation(self):
        """Test Task creation and defaults."""
        # Test with all parameters
        task1 = Task(name="test_task", args={"param": "value"}, value="result")
        assert task1.name == "test_task"
        assert task1.args == {"param": "value"}
        assert task1.value == "result"
        
        # Test with defaults
        task2 = Task(name="simple_task")
        assert task2.name == "simple_task"
        assert task2.args is None
        assert task2.value is None

    def test_yaml_config_validation_errors(self):
        """Test validation error handling for malformed files."""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            self.YAMLConfigWrapper("/non/existent/file.yaml")
            
        # Test with invalid schema path
        with pytest.raises(FileNotFoundError):
            YAMLConfig.validate("/non/existent/schema.json", self.create_temp_yaml(VALID_CONFIG_DATA["minimal"]))
