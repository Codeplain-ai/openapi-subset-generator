"""
Unit tests for the console application.
"""
import unittest
import os
import sys
from unittest.mock import patch, Mock
import generate_openapi_subset
from tests.test_data import create_mock_args
from tests.test_data import get_json_content
from tests.test_data import VALID_OPENAPI_SPEC


class TestMainModule(unittest.TestCase):
    """Test cases for the generate_openapi_subset module."""

    @patch('os.path.isfile')
    @patch('os.access')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.open')
    @patch('openapi_operations.output_openapi_spec_to_stdout')
    def test_main_success(self, mock_output, mock_open, mock_parse_args, mock_access, mock_isfile):
        """Test that the main function returns 0 on success."""
        # Mock the argument parser to return a valid file
        mock_parse_args.return_value = create_mock_args('valid_file.json')

        # Mock the open function to return test data
        mock_open.return_value.__enter__.return_value.read.return_value = get_json_content()

        # Mock file validation to succeed
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        result = generate_openapi_subset.main()
        self.assertEqual(result, 0)

    @patch('os.path.isfile')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_file_not_found(self, mock_parse_args, mock_isfile):
        """Test that the main function returns 1 when file doesn't exist."""
        # Mock the argument parser to return a non-existent file
        mock_parse_args.return_value = create_mock_args('nonexistent_file.json')

        # Mock file validation to fail
        mock_isfile.return_value = False
        
        result = generate_openapi_subset.main()
        self.assertEqual(result, 1)

    @patch('os.path.isfile')
    @patch('os.access')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_file_not_readable(self, mock_parse_args, mock_access, mock_isfile):
        """Test that the main function returns 1 when file is not readable."""
        # Mock the argument parser to return a file that exists but is not readable
        mock_parse_args.return_value = create_mock_args('unreadable_file.json')

        # Mock file validation: file exists but is not readable
        mock_isfile.return_value = True
        mock_access.return_value = False
        
        result = generate_openapi_subset.main()
        self.assertEqual(result, 1)

    @patch('generate_openapi_subset.parse_arguments')
    @patch('os.path.isfile')
    @patch('os.access')
    @patch('builtins.open')
    def test_main_with_args(self, mock_open, mock_access, mock_isfile, mock_parse_arguments):
        """Test that the main function returns 0 on success."""
        # Set up mocks to simulate a valid file
        mock_parse_arguments.return_value = create_mock_args('valid_file.json')
        mock_isfile.return_value = True
        mock_access.return_value = True

        # Mock the open function to return test data
        mock_open.return_value.__enter__.return_value.read.return_value = get_json_content()

        result = generate_openapi_subset.main()
        self.assertEqual(result, 0)

    @patch('generate_openapi_subset.setup_logging')
    @patch('generate_openapi_subset.parse_arguments')
    @patch('os.path.isfile', return_value=True)
    @patch('os.access', return_value=True)
    def test_logging_setup(self, mock_access, mock_isfile, mock_parse_arguments, mock_setup_logging):
        """Test that logging is set up correctly."""
        generate_openapi_subset.main()
        mock_setup_logging.assert_called_once()

    @patch('os.path.isfile')
    @patch('os.access')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.open')
    @patch('generate_openapi_subset.load_openapi_spec')
    @patch('generate_openapi_subset.output_openapi_spec_to_stdout')
    def test_main_outputs_to_stdout(self, mock_output, mock_load, mock_open, mock_parse_args, mock_access, mock_isfile):
        """Test that the main function outputs the OpenAPI spec to stdout."""
        # Mock the argument parser to return a valid file
        mock_parse_args.return_value = create_mock_args('valid_file.json')
        # Mock file validation to succeed
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        # Mock the open function to return test data
        mock_open.return_value.__enter__.return_value.read.return_value = get_json_content()
        # Mock the load function to return a valid spec
        mock_load.return_value = VALID_OPENAPI_SPEC
        
        generate_openapi_subset.main()
        mock_output.assert_called_once_with(VALID_OPENAPI_SPEC, use_yaml=False)
        
    @patch('os.path.isfile')
    @patch('os.access')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.open')
    @patch('generate_openapi_subset.load_openapi_spec')
    @patch('generate_openapi_subset.output_openapi_spec_to_stdout')
    def test_main_outputs_to_stdout_yaml(self, mock_output, mock_load, mock_open, mock_parse_args, mock_access, mock_isfile):
        """Test that the main function outputs the OpenAPI spec to stdout in YAML format when requested."""
        # Mock the argument parser to return a valid file with yaml flag
        mock_parse_args.return_value = create_mock_args('valid_file.json', yaml=True)
        # Mock file validation to succeed
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        # Mock the open function to return test data
        mock_open.return_value.__enter__.return_value.read.return_value = get_json_content()
        # Mock the load function to return a valid spec
        mock_load.return_value = VALID_OPENAPI_SPEC
        
        generate_openapi_subset.main()
        mock_output.assert_called_once_with(VALID_OPENAPI_SPEC, use_yaml=True)


if __name__ == '__main__':
    unittest.main()