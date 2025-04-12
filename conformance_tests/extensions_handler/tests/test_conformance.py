"""
Conformance tests for the OpenAPI subset generator application.
These tests verify that the application correctly removes OpenAPI extensions
when the --remove-extensions flag is provided.
"""
import unittest
import os
import json
import yaml
import tempfile
import subprocess
import shutil
import sys


class TestRemoveExtensions(unittest.TestCase):
    """Test cases for verifying the --remove-extensions functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def _get_app_path(self):
        """Get the path to the application."""
        # Use the current directory for the application
        app_dir = os.getcwd()
        return os.path.join(app_dir, "generate_openapi_subset.py")

    def _create_test_file(self, content, file_format='json'):
        """Create a test file with the given content."""
        file_path = os.path.join(self.test_dir, f"test_spec.{file_format}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_format == 'json':
                json.dump(content, f, indent=2)
            else:  # yaml
                yaml.dump(content, f)
                
        return file_path

    def _run_app_with_remove_extensions(self, input_file):
        """Run the application with the --remove-extensions flag."""
        result = subprocess.run(
            [sys.executable, self._get_app_path(), input_file, "--remove-extensions"],
            capture_output=True,
            check=False,
            text=True
        )
        return result, json.loads(result.stdout) if result.returncode == 0 else None

    def _load_file_content(self, file_path):
        """Load content from a file (JSON or YAML)."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if file_path.endswith('.json'):
            return json.loads(content)
        else:  # yaml
            return yaml.safe_load(content)

    def _check_no_extensions(self, data, path="root"):
        """
        Recursively check that no properties start with 'x-' in the data structure.
        Returns a list of paths where extensions were found.
        """
        extensions_found = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith('x-'):
                    extensions_found.append(f"{path}.{key}")
                extensions_found.extend(self._check_no_extensions(value, f"{path}.{key}"))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                extensions_found.extend(self._check_no_extensions(item, f"{path}[{i}]"))
                
        return extensions_found

    def test_simple_extension_removal(self):
        """Test that a simple extension is removed from the OpenAPI spec."""
        # Create a simple OpenAPI spec with an extension
        simple_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "x-extension": "This should be removed"
            },
            "paths": {}
        }
        
        # Create the test file
        test_file = self._create_test_file(simple_spec)
        
        # Run the application
        result, output_spec = self._run_app_with_remove_extensions(test_file)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Check the output spec
        self.assertIsNotNone(output_spec, "Failed to parse output JSON")
        
        # Check that the extension was removed
        self.assertNotIn('x-extension', output_spec['info'], 
                         "The x-extension property was not removed from the info object")
        
        # Check that other properties were preserved
        self.assertEqual(output_spec['info']['title'], "Test API", 
                         "The title property was not preserved")
        self.assertEqual(output_spec['info']['version'], "1.0.0", 
                         "The version property was not preserved")

    def test_preserve_non_extension_properties(self):
        """Test that non-extension properties are preserved when removing extensions."""
        # Create an OpenAPI spec with both extension and non-extension properties
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "This should be preserved",
                "x-logo": {"url": "https://example.com/logo.png"}
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "x-custom": "This should be removed",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }
        
        # Create the test file
        test_file = self._create_test_file(spec)
        
        # Run the application
        result, output_spec = self._run_app_with_remove_extensions(test_file)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Check the output spec
        self.assertIsNotNone(output_spec, "Failed to parse output JSON")
        
        # Check that extensions were removed
        self.assertNotIn('x-logo', output_spec['info'], 
                         "The x-logo extension was not removed")
        self.assertNotIn('x-custom', output_spec['paths']['/test']['get'], 
                         "The x-custom extension was not removed")
        
        # Check that non-extension properties were preserved
        self.assertEqual(output_spec['info']['description'], "This should be preserved", 
                         "The description property was not preserved")
        self.assertEqual(output_spec['paths']['/test']['get']['summary'], "Test endpoint", 
                         "The summary property was not preserved")

    def test_nested_extension_removal(self):
        """Test that nested extensions are removed from the OpenAPI spec."""
        # Create an OpenAPI spec with nested extensions
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "x-identifier": True
                            },
                            "name": {
                                "type": "string"
                            }
                        },
                        "x-discriminator": "type"
                    }
                }
            }
        }
        
        # Create the test file
        test_file = self._create_test_file(spec)
        
        # Run the application
        result, output_spec = self._run_app_with_remove_extensions(test_file)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Check the output spec
        self.assertIsNotNone(output_spec, "Failed to parse output JSON")
        
        # Check that nested extensions were removed
        extensions_found = self._check_no_extensions(output_spec)
        self.assertEqual(len(extensions_found), 0, 
                         f"Extensions were found at: {', '.join(extensions_found)}")
        
        # Check that the structure is preserved
        self.assertIn('components', output_spec, "The components object was not preserved")
        self.assertIn('schemas', output_spec['components'], "The schemas object was not preserved")
        self.assertIn('User', output_spec['components']['schemas'], "The User schema was not preserved")
        self.assertIn('properties', output_spec['components']['schemas']['User'], 
                      "The properties object was not preserved")
        self.assertIn('id', output_spec['components']['schemas']['User']['properties'], 
                      "The id property was not preserved")

    def test_extensions_in_arrays(self):
        """Test that extensions in arrays are properly removed."""
        # Create an OpenAPI spec with extensions in arrays
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "tags": [
                {
                    "name": "users",
                    "description": "User operations",
                    "x-display-name": "Users API"
                },
                {
                    "name": "items",
                    "description": "Item operations",
                    "x-display-name": "Items API"
                }
            ]
        }
        
        # Create the test file
        test_file = self._create_test_file(spec)
        
        # Run the application
        result, output_spec = self._run_app_with_remove_extensions(test_file)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Check the output spec
        self.assertIsNotNone(output_spec, "Failed to parse output JSON")
        
        # Check that extensions in arrays were removed
        for tag in output_spec['tags']:
            self.assertNotIn('x-display-name', tag, 
                             f"The x-display-name extension was not removed from tag {tag['name']}")
            
        # Check that other properties in arrays were preserved
        self.assertEqual(len(output_spec['tags']), 2, "The number of tags changed")
        self.assertEqual(output_spec['tags'][0]['name'], "users", "The name property was not preserved")
        self.assertEqual(output_spec['tags'][1]['description'], "Item operations", 
                         "The description property was not preserved")

    def test_with_asana_openapi_sample(self):
        """Test with the provided Asana OpenAPI sample."""
        # Path to the Asana OpenAPI sample
        asana_sample_path = "asana-openapi-sample.yaml"
        
        # Check if the sample file exists
        if not os.path.exists(asana_sample_path):
            self.skipTest(f"Asana OpenAPI sample file not found at {asana_sample_path}")
        
        # Copy the sample file to our test directory
        test_file = os.path.join(self.test_dir, "asana-sample.yaml")
        shutil.copy(asana_sample_path, test_file)
        
        # Run the application
        result, output_spec = self._run_app_with_remove_extensions(test_file)
        
        # Check that the application ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        # Check the output spec
        self.assertIsNotNone(output_spec, "Failed to parse output JSON")
        
        # Check that no extensions remain in the modified spec
        extensions_found = self._check_no_extensions(output_spec)
        self.assertEqual(len(extensions_found), 0, 
                         f"Extensions were found at: {', '.join(extensions_found)}")


if __name__ == '__main__':
    unittest.main()