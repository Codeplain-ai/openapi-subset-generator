"""
Conformance tests for YAML output functionality of the OpenAPI subset generator.
"""
import unittest
import os
import sys
import tempfile
import subprocess
import yaml
import json
from io import StringIO

class TestYamlOutput(unittest.TestCase):
    """Test cases for YAML output functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a simple OpenAPI spec for testing
        self.simple_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {
                            "200": {
                                "description": "OK"
                            }
                        }
                    }
                }
            }
        }

        # Create a temporary file to store the test OpenAPI spec
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.simple_spec, self.temp_file)
        self.temp_file.close()
        
        # Path to the Asana sample OpenAPI spec
        self.asana_sample_path = os.path.join(os.getcwd(), 'asana-openapi-sample.yaml')
        
        # Create the Asana sample file if it doesn't exist
        if not os.path.exists(self.asana_sample_path):
            with open(self.asana_sample_path, 'w') as f:
                f.write("""openapi: 3.0.0
info:
  description: >-
    This is the interface for interacting with the Asana Platform.
  title: Asana
  version: '1.0'
paths:
  /users/me:
    get:
      summary: Get the current user
      responses:
        '200':
          description: Successfully retrieved the user
""")

    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def run_app_with_args(self, args):
        """
        Run the application with the given arguments and return its output.
        
        Args:
            args: List of command-line arguments
            
        Returns:
            tuple: (stdout, stderr, return_code)
        """
        cmd = [sys.executable, 'generate_openapi_subset.py'] + args
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode

    def test_basic_yaml_output(self):
        """Test that the --yaml flag produces YAML output."""
        # Run the app with the --yaml flag
        stdout, stderr, return_code = self.run_app_with_args([self.temp_file.name, '--yaml'])
        
        # Check that the command succeeded
        self.assertEqual(return_code, 0, f"Application failed with stderr: {stderr}")
        
        # Verify the output starts with YAML indicators (not JSON's '{')
        self.assertFalse(stdout.strip().startswith('{'), 
                         "Output appears to be JSON, not YAML")
        
        # Try to parse the output as YAML
        try:
            parsed_output = yaml.safe_load(stdout)
            # Verify the parsed output matches our input
            self.assertEqual(parsed_output['openapi'], self.simple_spec['openapi'],
                            "YAML output doesn't match expected structure")
        except yaml.YAMLError as e:
            self.fail(f"Failed to parse output as YAML: {e}")

    def test_yaml_format_validation(self):
        """Test that the YAML output can be parsed back into the original structure."""
        # Run the app with the --yaml flag
        stdout, stderr, return_code = self.run_app_with_args([self.temp_file.name, '--yaml'])
        
        # Check that the command succeeded
        self.assertEqual(return_code, 0, f"Application failed with stderr: {stderr}")
        
        # Parse the output as YAML
        try:
            parsed_yaml = yaml.safe_load(stdout)
            
            # Compare with the original spec
            self.assertEqual(parsed_yaml, self.simple_spec,
                            "Parsed YAML doesn't match the original spec")
        except yaml.YAMLError as e:
            self.fail(f"Failed to parse output as YAML: {e}")

    def test_unquoted_keys(self):
        """Test that keys in the YAML output are not quoted by default."""
        # Run the app with the --yaml flag
        stdout, stderr, return_code = self.run_app_with_args([self.temp_file.name, '--yaml'])
        
        # Check that the command succeeded
        self.assertEqual(return_code, 0, f"Application failed with stderr: {stderr}")
        
        # Check for quoted keys in the output
        # In YAML, quoted keys would look like: '"key": value' or "'key': value"
        lines = stdout.strip().split('\n')
        for line in lines:
            if ':' in line:  # Only check lines with key-value pairs
                key_part = line.split(':', 1)[0].strip()
                
                # Skip numeric keys - they are typically quoted in YAML
                # Remove quotes to check if the content is numeric
                unquoted_key = key_part.strip("'\"")
                if unquoted_key.isdigit():
                    continue
                    
                # Check if non-numeric keys are quoted
                self.assertFalse(
                    (key_part.startswith('"') and key_part.endswith('"')) or
                    (key_part.startswith("'") and key_part.endswith("'")),
                    f"Found quoted key in YAML output: {line}"
                )

    def test_complex_structure(self):
        """Test YAML output with a more complex OpenAPI structure."""
        # Run the app with the Asana sample and the --yaml flag
        stdout, stderr, return_code = self.run_app_with_args([self.asana_sample_path, '--yaml'])
        
        # Check that the command succeeded
        self.assertEqual(return_code, 0, f"Application failed with stderr: {stderr}")
        
        # Try to parse the output as YAML
        try:
            parsed_yaml = yaml.safe_load(stdout)
            
            # Verify some key elements from the Asana sample
            self.assertEqual(parsed_yaml['openapi'], '3.0.0',
                            "YAML output doesn't contain expected OpenAPI version")
            self.assertEqual(parsed_yaml['info']['title'], 'Asana',
                            "YAML output doesn't contain expected API title")
        except yaml.YAMLError as e:
            self.fail(f"Failed to parse complex YAML output: {e}")

    def test_combined_options(self):
        """Test YAML output when combined with other options."""
        # Create a spec with descriptions and extensions
        spec_with_extras = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "This should be removed",
                "x-extension": "This should also be removed"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "description": "Another description to remove",
                        "responses": {
                            "200": {
                                "description": "OK"
                            }
                        }
                    }
                }
            }
        }
        
        # Create a temporary file for this test
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(spec_with_extras, temp_file)
        temp_file.close()
        
        try:
            # Run the app with all options
            stdout, stderr, return_code = self.run_app_with_args([
                temp_file.name, 
                '--yaml', 
                '--remove-descriptions', 
                '--remove-extensions'
            ])
            
            # Check that the command succeeded
            self.assertEqual(return_code, 0, f"Application failed with stderr: {stderr}")
            
            # Parse the output as YAML
            parsed_yaml = yaml.safe_load(stdout)
            
            # Verify descriptions are removed
            self.assertNotIn('description', parsed_yaml['info'], 
                            "Description not removed from info object")
            
            # Verify extensions are removed
            self.assertNotIn('x-extension', parsed_yaml['info'], 
                            "Extension not removed from info object")
            
            # Verify the output is in YAML format
            self.assertFalse(stdout.strip().startswith('{'), 
                            "Output appears to be JSON, not YAML")
        finally:
            # Clean up
            os.unlink(temp_file.name)
            
if __name__ == '__main__':
    unittest.main()