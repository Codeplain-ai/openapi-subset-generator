"""
Conformance tests for the OpenAPI subset generator application.
These tests verify that the application correctly removes descriptions
from OpenAPI specifications when the --remove-descriptions flag is provided.
"""
import unittest
import os
import subprocess
import tempfile
import json
import yaml
import shutil
import sys


class TestRemoveDescriptions(unittest.TestCase):
    """Test cases for the --remove-descriptions functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Path to the application
        self.app_path = "generate_openapi_subset.py"
        
        # Ensure the application exists
        self.assertTrue(os.path.exists(self.app_path), 
                        f"Application not found at {self.app_path}")

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def _create_test_file(self, content, filename):
        """Create a test file with the given content."""
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            if filename.endswith('.json'):
                json.dump(content, f, indent=2)
            else:  # yaml
                yaml.dump(content, f)
        return file_path

    def _run_app(self, input_file, remove_descriptions=False):
        """Run the application on the input file."""
        cmd = ["python", self.app_path, input_file]
        if remove_descriptions:
            cmd.append("--remove-descriptions")

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result

    def _load_file(self, file_path):
        """Load a file and return its content as a dictionary."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if file_path.endswith('.json'):
                return json.loads(content)
            else:  # yaml
                return yaml.safe_load(content)

    def _parse_stdout(self, stdout_content):
        """Parse the stdout content as JSON."""
        try:
            return json.loads(stdout_content)
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse stdout as JSON: {e}\nContent: {stdout_content}")
            return None

    def _has_descriptions(self, data):
        """Check if the data contains any description fields."""
        if isinstance(data, dict):
            if 'description' in data:
                return True
            return any(self._has_descriptions(value) for value in data.values())
        elif isinstance(data, list):
            return any(self._has_descriptions(item) for item in data)
        return False

    def test_basic_remove_descriptions(self):
        """Test that basic descriptions are removed when flag is provided."""
        # Create a simple OpenAPI spec with descriptions
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "This is a test API"
            },
            "paths": {
                "/test": {
                    "get": {
                        "description": "Test endpoint",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }
        
        # Create test file
        test_file = self._create_test_file(spec, "basic_test.json")
        
        # Run application with --remove-descriptions flag and capture stdout
        result = self._run_app(test_file, remove_descriptions=True)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Parse the stdout output
        modified_spec = self._parse_stdout(result.stdout)
        
        # Verify descriptions were removed
        self.assertFalse(self._has_descriptions(modified_spec),
                         "Descriptions were not removed from the spec")
        
        # Verify structure is preserved
        self.assertEqual(modified_spec["openapi"], "3.0.0")
        self.assertEqual(modified_spec["info"]["title"], "Test API")
        self.assertEqual(modified_spec["info"]["version"], "1.0.0")
        self.assertIn("paths", modified_spec)
        self.assertIn("/test", modified_spec["paths"])
        self.assertIn("get", modified_spec["paths"]["/test"])
        self.assertIn("responses", modified_spec["paths"]["/test"]["get"])
        self.assertIn("200", modified_spec["paths"]["/test"]["get"]["responses"])

    def test_nested_descriptions(self):
        """Test that deeply nested descriptions are removed."""
        # Create a spec with nested descriptions
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Nested API",
                "version": "1.0.0",
                "description": "Top level description"
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "description": "User schema",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "User ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "User name"
                            },
                            "address": {
                                "type": "object",
                                "description": "User address",
                                "properties": {
                                    "street": {
                                        "type": "string",
                                        "description": "Street name"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Create test file
        test_file = self._create_test_file(spec, "nested_test.json")
        
        # Run application with --remove-descriptions flag and capture stdout
        result = self._run_app(test_file, remove_descriptions=True)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Parse the stdout output
        modified_spec = self._parse_stdout(result.stdout)
        
        # Verify descriptions were removed
        self.assertFalse(self._has_descriptions(modified_spec),
                         "Nested descriptions were not removed from the spec")
        
        # Verify structure is preserved
        self.assertIn("components", modified_spec)
        self.assertIn("schemas", modified_spec["components"])
        self.assertIn("User", modified_spec["components"]["schemas"])
        self.assertIn("properties", modified_spec["components"]["schemas"]["User"])
        self.assertIn("address", modified_spec["components"]["schemas"]["User"]["properties"])
        self.assertIn("properties", modified_spec["components"]["schemas"]["User"]["properties"]["address"])
        self.assertIn("street", modified_spec["components"]["schemas"]["User"]["properties"]["address"]["properties"])

    def test_preserve_descriptions_without_flag(self):
        """Test that descriptions are preserved when flag is not provided."""
        # Create a simple OpenAPI spec with descriptions
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "This is a test API"
            }
        }
        
        # Create test file
        test_file = self._create_test_file(spec, "preserve_test.json")
        
        # Run application without --remove-descriptions flag and capture stdout
        result = self._run_app(test_file, remove_descriptions=False)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Parse the stdout output
        modified_spec = self._parse_stdout(result.stdout)
        
        # Verify descriptions were preserved
        self.assertTrue(self._has_descriptions(modified_spec),
                        "Descriptions were removed when they should be preserved")
        
        # Verify specific description is present
        self.assertEqual(modified_spec["info"]["description"], "This is a test API",
                         "Description content was modified")

    def test_asana_openapi_sample(self):
        """Test with the Asana OpenAPI sample."""
        # Create the Asana OpenAPI sample content
        asana_sample_content = """openapi: 3.0.0
info:
  description: >-
    This is the interface for interacting with the [Asana
    Platform](https://developers.asana.com). Our API reference
    is generated from our [OpenAPI spec]
    (https://raw.githubusercontent.com/Asana/openapi/master/defs/asana_oas.yaml).
  title: Asana
  version: '1.0'
tags:
  - name: Allocations
    description: An allocation object represents how much of a resource is dedicated to a specific work object."""

        # Create the test file directly in our test directory
        test_file = os.path.join(self.test_dir, "asana-test.yaml")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(asana_sample_content)
        
        # Load the original file to verify it has descriptions before processing
        original_spec = self._load_file(test_file)
        self.assertTrue(self._has_descriptions(original_spec),
                        "Original Asana sample doesn't contain descriptions")
        
        # Run application with --remove-descriptions flag and capture stdout
        result = self._run_app(test_file, remove_descriptions=True)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Parse the stdout output
        modified_spec = self._parse_stdout(result.stdout)
        
        # Verify descriptions were removed from stdout output
        self.assertFalse(self._has_descriptions(modified_spec),
                         "Descriptions were not removed from the Asana sample")

        # Verify structure is preserved (check a few key elements)
        self.assertEqual(modified_spec["openapi"], original_spec["openapi"])
        self.assertEqual(modified_spec["info"]["title"], original_spec["info"]["title"])
        self.assertEqual(modified_spec["info"]["version"], original_spec["info"]["version"])
        self.assertIn("tags", modified_spec, "Tags section is missing from the output")


if __name__ == '__main__':
    unittest.main()