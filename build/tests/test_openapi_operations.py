"""
Unit tests for OpenAPI operations in the generate_openapi_subset module.
"""
import unittest
import json
import yaml
import sys
from unittest.mock import patch, mock_open, MagicMock
from openapi_operations import load_openapi_spec, remove_descriptions, remove_extensions, save_openapi_spec
from tests.test_data import (
    VALID_OPENAPI_SPEC,
    OPENAPI_SPEC_WITHOUT_DESCRIPTIONS,
    OPENAPI_SPEC_WITHOUT_EXTENSIONS,
    get_json_content,
    get_yaml_content,
    get_invalid_content
)

# Import the new function
from openapi_operations import output_openapi_spec_to_stdout

class TestOpenAPIOperations(unittest.TestCase):
    """Test cases for OpenAPI operations in the generate_openapi_subset module."""

    def test_load_openapi_spec_json(self):
        """Test loading an OpenAPI spec from a JSON file."""
        # Create a mock file with JSON content
        mock_open_instance = mock_open(read_data=get_json_content())
        
        with patch('builtins.open', mock_open_instance):
            result = load_openapi_spec('test.json')
            self.assertEqual(result, VALID_OPENAPI_SPEC)

    def test_load_openapi_spec_yaml(self):
        """Test loading an OpenAPI spec from a YAML file."""
        # Create a mock file with YAML content
        mock_open_instance = mock_open(read_data=get_yaml_content())
        
        with patch('builtins.open', mock_open_instance):
            result = load_openapi_spec('test.yaml')
            self.assertEqual(result, VALID_OPENAPI_SPEC)

    def test_load_openapi_spec_invalid(self):
        """Test loading an invalid OpenAPI spec."""
        # Create a mock file with invalid content
        mock_open_instance = mock_open(read_data=get_invalid_content())
        
        with patch('builtins.open', mock_open_instance):
            with self.assertRaises(ValueError):
                load_openapi_spec('test.json')

    def test_remove_descriptions(self):
        """Test removing description fields from an OpenAPI spec."""
        result = remove_descriptions(VALID_OPENAPI_SPEC)
        self.assertEqual(result, OPENAPI_SPEC_WITHOUT_DESCRIPTIONS)

    def test_remove_extensions(self):
        """Test removing extension fields (starting with x-) from an OpenAPI spec."""
        result = remove_extensions(VALID_OPENAPI_SPEC)
        self.assertEqual(result, OPENAPI_SPEC_WITHOUT_EXTENSIONS)
        # Verify that all x- properties are removed
        self.assertNotIn('x-logo', result['info'])

    @patch('json.dump')
    def test_save_openapi_spec_json(self, mock_json_dump):
        """Test saving an OpenAPI spec to a JSON file."""
        test_spec = {"openapi": "3.0.0"}
        
        with patch('builtins.open', mock_open()):
            save_openapi_spec(test_spec, 'test.json')
            mock_json_dump.assert_called_once()

    @patch('yaml.dump')
    def test_save_openapi_spec_yaml(self, mock_yaml_dump):
        """Test saving an OpenAPI spec to a YAML file."""
        test_spec = {"openapi": "3.0.0"}
        
        with patch('builtins.open', mock_open()):
            save_openapi_spec(test_spec, 'test.yaml')
            mock_yaml_dump.assert_called_once()

    @patch('json.dump')
    def test_output_openapi_spec_to_stdout(self, mock_json_dump):
        """Test outputting an OpenAPI spec to stdout in JSON format."""
        test_spec = {"openapi": "3.0.0"}
        
        # Call the function
        output_openapi_spec_to_stdout(test_spec)
        
        # Verify json.dump was called with the spec and sys.stdout
        mock_json_dump.assert_called_once_with(test_spec, sys.stdout, indent=2)

    @patch('yaml.dump')
    def test_output_openapi_spec_to_stdout_yaml(self, mock_yaml_dump):
        """Test outputting an OpenAPI spec to stdout in YAML format."""
        test_spec = {"openapi": "3.0.0"}
        
        # Call the function with use_yaml=True
        output_openapi_spec_to_stdout(test_spec, use_yaml=True)
        
        # Verify yaml.dump was called with the spec and sys.stdout
        mock_yaml_dump.assert_called_once_with(test_spec, sys.stdout, sort_keys=False, default_flow_style=False)


if __name__ == '__main__':
    unittest.main()