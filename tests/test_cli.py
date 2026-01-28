import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, MagicMock
import argparse

from model_ensembler.cli import parse_indexes, parse_args, main, check
from model_ensembler.utils import Arguments


class TestParseIndexes:
    """Test the parse_indexes function."""
    
    def test_valid_single_index(self):
        """Test parsing a single valid index."""
        result = parse_indexes("5")
        assert result == [5]
    
    def test_valid_multiple_indexes(self):
        """Test parsing multiple valid indexes."""
        result = parse_indexes("1,3,5,10")
        assert result == [1, 3, 5, 10]
    
    def test_valid_two_indexes(self):
        """Test parsing two valid indexes."""
        result = parse_indexes("0,1")
        assert result == [0, 1]
    
    @pytest.mark.parametrize("invalid_input", [
        "a,b,c",           # Non-numeric
        "1,2,",            # Trailing comma
        ",1,2",            # Leading comma
        "1,,2",            # Double comma
        "1.5,2",           # Float values
        "",                # Empty string
        "1 2 3",           # Space separated
        "1;2;3",           # Semicolon separated
    ])
    def test_invalid_indexes(self, invalid_input):
        """Test that invalid index formats raise ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError, match="is not a CSV delimited integer list"):
            parse_indexes(invalid_input)


class TestParseArgs:
    """Test the parse_args function."""
    
    def setup_method(self):
        """Reset Arguments singleton before each test."""
        Arguments.instance = None
    
    def test_minimal_args(self):
        """Test parsing minimal required arguments."""
        args = parse_args(["config.yml", "dummy"])
        assert args.configuration == "config.yml"
        assert args.backend == "dummy"
        assert args.daemon is False
        assert args.verbose is False
    
    def test_all_boolean_flags(self):
        """Test all boolean flags are properly parsed."""
        args = parse_args([
            "-d", "-v", "-c", "-s", "-p",
            "config.yml", "slurm"
        ])
        assert args.daemon is True
        assert args.verbose is True
        assert args.no_checks is True
        assert args.no_submission is True
        assert args.pickup is True
    
    def test_backend_choices(self):
        """Test that valid backend choices are accepted."""
        args_slurm = parse_args(["config.yml", "slurm"])
        assert args_slurm.backend == "slurm"
        
        # Reset singleton for second test
        Arguments.instance = None
        args_dummy = parse_args(["config.yml", "dummy"])
        assert args_dummy.backend == "dummy"
    
    def test_default_backend(self):
        """Test default backend when not specified."""
        args = parse_args(["config.yml"])
        assert args.backend == "slurm"
    
    def test_timeout_arguments(self):
        """Test timeout argument parsing."""
        args = parse_args([
            "-ct", "60", "-st", "40", "-rt", "120", "-et", "240",
            "config.yml", "dummy"
        ])
        assert args.check_timeout == 60
        assert args.submit_timeout == 40
        assert args.running_timeout == 120
        assert args.error_timeout == 240
    
    def test_skip_and_index_arguments(self):
        """Test skip and index argument parsing."""
        args = parse_args([
            "-k", "5", "-i", "1,3,7", "-ms", "3",
            "config.yml", "dummy"
        ])
        assert args.skips == 5
        assert args.indexes == [1, 3, 7]
        assert args.max_stagger == 3
    
    def test_shell_argument(self):
        """Test shell argument parsing."""
        args = parse_args(["-l", "/bin/zsh", "config.yml", "dummy"])
        assert args.shell == "/bin/zsh"
    
    def test_extra_vars_parsing(self):
        """Test extra variables parsing."""
        args = parse_args([
            "config.yml", "dummy", "-x", "key1=value1", "key2=value2"
        ])
        assert args.extra == [("key1", "value1"), ("key2", "value2")]
    
    def test_no_args_list_uses_sys_argv(self):
        """Test that when args_list is None, sys.argv is used."""
        with patch('sys.argv', ['model_ensemble', 'config.yml', 'dummy']):
            args = parse_args()
            assert args.configuration == "config.yml"
            assert args.backend == "dummy"
    
    def test_arguments_return_type(self):
        """Test that parse_args returns Arguments instance."""
        args = parse_args(["config.yml", "dummy"])
        assert isinstance(args, Arguments)
    
    def test_long_form_arguments(self):
        """Test long-form argument parsing."""
        args = parse_args([
            "--daemon", "--verbose", "--no-checks", "--no-submission", "--pickup",
            "--shell", "/bin/bash", "--skips", "2", "--max-stagger", "4",
            "--check-timeout", "45", "--submit-timeout", "25",
            "--running-timeout", "90", "--error-timeout", "180",
            "config.yml", "slurm"
        ])
        assert args.daemon is True
        assert args.verbose is True
        assert args.no_checks is True
        assert args.no_submission is True
        assert args.pickup is True
        assert args.shell == "/bin/bash"
        assert args.skips == 2
        assert args.max_stagger == 4


class TestMain:
    """Test the main function."""
    
    @staticmethod
    def create_temp_config():
        """Create a temporary valid config file."""
        config_data = {
            "ensemble": {
                "batches": [{
                    "name": "test_batch",
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
        }
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w") as f:
            yaml.dump(config_data, f)
        return path
    
    @patch('model_ensembler.cli.BatchExecutor')
    @patch('model_ensembler.cli.EnsembleConfig')
    @patch('model_ensembler.cli.setup_logging')
    @patch('model_ensembler.cli.background_fork')
    def test_main_with_daemon(self, mock_fork, mock_logging, mock_config, mock_executor):
        """Test main function with daemon mode."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.daemon = True
        mock_args.verbose = False
        mock_args.configuration = "test.yml"
        mock_args.backend = "dummy"
        mock_args.extra = []
        
        # Call main
        main(mock_args)
        
        # Verify daemon fork was called
        mock_fork.assert_called_once_with(True)
        
        # Verify logging setup
        mock_logging.assert_called_once_with("test.yml", verbose=False)
        
        # Verify config and executor setup
        mock_config.assert_called_once_with("test.yml")
        mock_executor.assert_called_once()
        mock_executor.return_value.run.assert_called_once()
    
    @patch('model_ensembler.cli.BatchExecutor')
    @patch('model_ensembler.cli.EnsembleConfig')
    @patch('model_ensembler.cli.setup_logging')
    @patch('model_ensembler.cli.background_fork')
    def test_main_without_daemon(self, mock_fork, mock_logging, mock_config, mock_executor):
        """Test main function without daemon mode."""
        mock_args = MagicMock()
        mock_args.daemon = False
        mock_args.verbose = True
        mock_args.configuration = "test.yml"
        mock_args.backend = "slurm"
        mock_args.extra = [("key", "value")]
        
        main(mock_args)
        
        # Verify daemon fork was NOT called
        mock_fork.assert_not_called()
        
        # Verify logging setup with verbose
        mock_logging.assert_called_once_with("test.yml", verbose=True)
        
        # Verify executor called with extra vars
        mock_executor.assert_called_once_with(
            mock_config.return_value, "slurm", {"key": "value"}
        )
    
    @patch('model_ensembler.cli.parse_args')
    @patch('model_ensembler.cli.BatchExecutor')
    @patch('model_ensembler.cli.EnsembleConfig')
    @patch('model_ensembler.cli.setup_logging')
    def test_main_with_none_args(self, mock_logging, mock_config, mock_executor, mock_parse):
        """Test main function when args is None (uses parse_args)."""
        # Setup mock parse_args return
        mock_args = MagicMock()
        mock_args.daemon = False
        mock_args.verbose = False
        mock_args.configuration = "parsed.yml"
        mock_args.backend = "dummy"
        mock_args.extra = []
        mock_parse.return_value = mock_args
        
        main(None)
        
        # Verify parse_args was called
        mock_parse.assert_called_once()
        
        # Verify rest of execution
        mock_config.assert_called_once_with("parsed.yml")
        mock_executor.assert_called_once()
    
    @patch('model_ensembler.cli.BatchExecutor')
    @patch('model_ensembler.cli.EnsembleConfig') 
    @patch('model_ensembler.cli.setup_logging')
    def test_main_basename_extraction(self, mock_logging, mock_config, mock_executor):
        """Test that main extracts basename from configuration path for logging."""
        mock_args = MagicMock()
        mock_args.daemon = False
        mock_args.verbose = False
        mock_args.configuration = "/long/path/to/config.yml"
        mock_args.backend = "dummy"
        mock_args.extra = []
        
        main(mock_args)
        
        # Verify logging was called with basename only
        mock_logging.assert_called_once_with("config.yml", verbose=False)


class TestCheck:
    """Test the check function."""
    
    @patch('model_ensembler.cli.main')
    @patch('model_ensembler.cli.parse_args')
    @patch('sys.argv', ['model_ensemble_check', 'dummy'])
    def test_check_function(self, mock_parse, mock_main):
        """Test check function combines sanity config with user args."""
        mock_args = MagicMock()
        mock_parse.return_value = mock_args
        
        check()
        
        # Verify parse_args called with sanity check config + user args
        mock_parse.assert_called_once_with(["examples/sanity-check.yml", "dummy"])
        
        # Verify main called with parsed args
        mock_main.assert_called_once_with(mock_args)
    
    @patch('model_ensembler.cli.main')
    @patch('model_ensembler.cli.parse_args')
    @patch('sys.argv', ['model_ensemble_check', '--verbose', 'slurm'])
    def test_check_with_extra_args(self, mock_parse, mock_main):
        """Test check function with additional user arguments."""
        mock_args = MagicMock()
        mock_parse.return_value = mock_args
        
        check()
        
        # Verify parse_args called with sanity config + all user args
        mock_parse.assert_called_once_with([
            "examples/sanity-check.yml", "--verbose", "slurm"
        ])
        
        mock_main.assert_called_once_with(mock_args)
    
    @patch('model_ensembler.cli.main')
    @patch('model_ensembler.cli.parse_args')
    @patch('sys.argv', ['model_ensemble_check'])
    def test_check_no_user_args(self, mock_parse, mock_main):
        """Test check function with no additional user arguments."""
        mock_args = MagicMock()
        mock_parse.return_value = mock_args
        
        check()
        
        # Verify parse_args called with just sanity config
        mock_parse.assert_called_once_with(["examples/sanity-check.yml"])
        
        mock_main.assert_called_once_with(mock_args)


class TestArgumentsIntegration:
    """Test Arguments class integration with CLI parsing."""
    
    def setup_method(self):
        """Reset Arguments singleton before each test."""
        Arguments.instance = None
    
    def test_arguments_singleton_behavior(self):
        """Test that Arguments maintains singleton behavior."""
        # Create first instance
        args1 = parse_args(["config1.yml", "dummy"])
        
        # Create a new Arguments object (should reference same singleton)
        args2 = Arguments()
        
        # Both should reference the same singleton instance
        assert args1.instance is args2.instance
        
        # Both should have the same values (from the first parse_args call)
        assert args1.configuration == args2.configuration == "config1.yml"
        assert args1.backend == args2.backend == "dummy"
    
    def test_arguments_singleton_reset(self):
        """Test that resetting the singleton allows new values."""
        # Create first instance
        args1 = parse_args(["config1.yml", "dummy"])
        assert args1.configuration == "config1.yml"
        
        # Reset singleton and create new instance
        Arguments.instance = None
        args2 = parse_args(["config2.yml", "slurm"])
        
        # New instance should have new values
        assert args2.configuration == "config2.yml"
        assert args2.backend == "slurm"
    
    def test_arguments_attribute_access(self):
        """Test that Arguments allows proper attribute access."""
        args = parse_args([
            "--verbose", "--daemon", "-k", "3",
            "test.yml", "dummy"
        ])
        
        # Test various attribute types
        assert args.verbose is True
        assert args.daemon is True
        assert args.skips == 3
        assert args.configuration == "test.yml"
        assert args.backend == "dummy"
        assert isinstance(args.extra, list)
        
        # Test defaults
        assert args.no_checks is False
        assert args.shell == "/bin/bash"
        assert args.check_timeout == 30


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""
    
    def test_invalid_backend_choice(self):
        """Test that invalid backend choices raise SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["config.yml", "invalid_backend"])
    
    def test_missing_configuration_argument(self):
        """Test that missing configuration argument raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_args([])
    
    def test_invalid_timeout_values(self):
        """Test that invalid timeout values raise SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["-ct", "not_a_number", "config.yml", "dummy"])
    
    def test_invalid_skip_value(self):
        """Test that invalid skip values raise SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["-k", "not_a_number", "config.yml", "dummy"])


class TestCLIDefaults:
    """Test CLI default values."""
    
    def setup_method(self):
        """Reset Arguments singleton before each test."""
        Arguments.instance = None
    
    def test_all_defaults(self):
        """Test that all arguments have appropriate defaults."""
        args = parse_args(["config.yml"])
        
        # Boolean defaults
        assert args.daemon is False
        assert args.verbose is False
        assert args.no_checks is False
        assert args.no_submission is False
        assert args.pickup is False
        
        # String defaults
        assert args.shell == "/bin/bash"
        assert args.backend == "slurm"  # Default when not specified
        
        # Integer defaults
        assert args.skips == 0
        assert args.check_timeout == 30
        assert args.submit_timeout == 20
        assert args.running_timeout == 60
        assert args.error_timeout == 120
        assert args.max_stagger == 1
        
        # List defaults
        assert args.extra == []
        assert args.indexes is None  # No default for indexes
