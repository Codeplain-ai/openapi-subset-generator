"""
Conformance tests for the OpenAPI subset generator application.
These tests verify that the application correctly outputs OpenAPI subsets in JSON format.
"""
import unittest
import json
import os
import subprocess
import tempfile
import yaml

__unittest = True  # This helps unittest discover this module

class TestOpenAPISubsetOutput(unittest.TestCase):
    """Test cases for verifying the JSON output of the OpenAPI subset generator."""

    def setUp(self):
        """Set up test environment."""
        # Ensure we're in the correct directory
        self.app_path = "generate_openapi_subset.py"
        self.assertTrue(os.path.exists(self.app_path), 
                        f"Application file {self.app_path} not found in current directory")

    def run_app(self, input_file, remove_descriptions=False, remove_extensions=False):
        """
        Run the application with the given input file and options.
        
        Args:
            input_file: Path to the input OpenAPI spec file
            remove_descriptions: Whether to pass the --remove-descriptions flag
            remove_extensions: Whether to pass the --remove-extensions flag
            
        Returns:
            tuple: (return_code, stdout_content, stderr_content)
        """
        cmd = ["python", self.app_path, input_file]
        
        if remove_descriptions:
            cmd.append("--remove-descriptions")
        
        if remove_extensions:
            cmd.append("--remove-extensions")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def test_basic_json_output(self):
        """Test that the application outputs valid JSON to stdout."""
        # Create a temporary file with a simple OpenAPI spec
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_file.write(json.dumps({
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"}
            }).encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Run the application
            return_code, stdout, stderr = self.run_app(temp_file_path)
            
            # Check return code
            self.assertEqual(return_code, 0, 
                            f"Application failed with return code {return_code}. Stderr: {stderr}")
            
            # Check that output is valid JSON
            try:
                output_json = json.loads(stdout)
                self.assertIsInstance(output_json, dict, 
                                    "Output JSON is not a dictionary")
                
                # Check that the output contains the expected fields
                self.assertEqual(output_json["openapi"], "3.0.0", 
                                "Output JSON does not contain expected 'openapi' field")
                self.assertEqual(output_json["info"]["title"], "Test API", 
                                "Output JSON does not contain expected 'info.title' field")
            except json.JSONDecodeError as e:
                self.fail(f"Output is not valid JSON: {e}\nOutput: {stdout}")
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_format_preservation(self):
        """Test that the output JSON maintains the same structure as the input."""
        # Create a temporary file with a more complex OpenAPI spec
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }
        
        # Test with both JSON and YAML input
        for file_ext, file_content in [
            ('.json', json.dumps(spec)),
            ('.yaml', yaml.dump(spec))
        ]:
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                temp_file.write(file_content.encode('utf-8'))
                temp_file_path = temp_file.name
            
            try:
                # Run the application
                return_code, stdout, stderr = self.run_app(temp_file_path)
                
                # Check return code
                self.assertEqual(return_code, 0, 
                                f"Application failed with {file_ext} input. Return code: {return_code}. Stderr: {stderr}")
                
                # Check that output is valid JSON
                try:
                    output_json = json.loads(stdout)
                    
                    # Check structure preservation
                    self.assertEqual(output_json["openapi"], spec["openapi"], 
                                    f"Output JSON with {file_ext} input does not preserve 'openapi' field")
                    self.assertEqual(output_json["info"]["title"], spec["info"]["title"], 
                                    f"Output JSON with {file_ext} input does not preserve 'info.title' field")
                    self.assertEqual(output_json["paths"]["/test"]["get"]["summary"], 
                                    spec["paths"]["/test"]["get"]["summary"],
                                    f"Output JSON with {file_ext} input does not preserve nested fields")
                except json.JSONDecodeError as e:
                    self.fail(f"Output with {file_ext} input is not valid JSON: {e}\nOutput: {stdout}")
            finally:
                # Clean up
                os.unlink(temp_file_path)

    def test_command_line_options(self):
        """Test that command line options correctly modify the output."""
        # Create a temporary file with a spec that has descriptions and extensions
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API",
                "x-logo": {"url": "https://example.com/logo.png"}
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "description": "This is a test endpoint",
                        "x-custom": "value",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_file.write(json.dumps(spec).encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Test with --remove-descriptions
            return_code, stdout, stderr = self.run_app(temp_file_path, remove_descriptions=True)
            self.assertEqual(return_code, 0, 
                            f"Application failed with --remove-descriptions. Return code: {return_code}. Stderr: {stderr}")
            
            output_json = json.loads(stdout)
            self.assertNotIn("description", output_json["info"], 
                            "Description not removed from info object")
            self.assertNotIn("description", output_json["paths"]["/test"]["get"], 
                            "Description not removed from path operation")
            
            # Test with --remove-extensions
            return_code, stdout, stderr = self.run_app(temp_file_path, remove_extensions=True)
            self.assertEqual(return_code, 0, 
                            f"Application failed with --remove-extensions. Return code: {return_code}. Stderr: {stderr}")
            
            output_json = json.loads(stdout)
            self.assertNotIn("x-logo", output_json["info"], 
                            "Extension not removed from info object")
            self.assertNotIn("x-custom", output_json["paths"]["/test"]["get"], 
                            "Extension not removed from path operation")
            
            # Test with both options
            return_code, stdout, stderr = self.run_app(
                temp_file_path, remove_descriptions=True, remove_extensions=True
            )
            self.assertEqual(return_code, 0, 
                            f"Application failed with both options. Return code: {return_code}. Stderr: {stderr}")
            
            output_json = json.loads(stdout)
            self.assertNotIn("description", output_json["info"], 
                            "Description not removed with both options")
            self.assertNotIn("x-logo", output_json["info"], 
                            "Extension not removed with both options")
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_real_world_example(self):
        """Test the application with a real-world OpenAPI spec."""
        # Check if the Asana sample exists
        asana_sample_path = "asana-openapi-sample.yaml"
        
        if not os.path.exists(asana_sample_path):
            # Create a minimal OpenAPI spec for testing if the sample doesn't exist
            with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
                minimal_spec = {
                    "openapi": "3.0.0",
                    "info": {"title": "Asana", "version": "1.0"},
                    "paths": {},
                    "components": {"schemas": {}}
                }
                temp_file.write(yaml.dump(minimal_spec).encode('utf-8'))
                asana_sample_path = temp_file.name
        
        if not os.path.exists(asana_sample_path):
            self.skipTest(f"Asana sample file {asana_sample_path} not found")
        
        # Run the application with the Asana sample
        return_code, stdout, stderr = self.run_app(asana_sample_path)
        
        # Check return code
        self.assertEqual(return_code, 0, 
                        f"Application failed with Asana sample. Return code: {return_code}. Stderr: {stderr}")
        
        # Check that output is valid JSON
        try:
            output_json = json.loads(stdout)
            
            # Check that the output contains expected Asana-specific fields
            self.assertEqual(output_json["info"]["title"], "Asana", 
                           "Output JSON does not contain expected Asana title")
            self.assertIn("paths", output_json, 
                         "Output JSON does not contain 'paths' section from Asana sample")
            self.assertIn("components", output_json, 
                         "Output JSON does not contain 'components' section from Asana sample")
        except json.JSONDecodeError as e:
            self.fail(f"Output with Asana sample is not valid JSON: {e}\nOutput: {stdout}")
        finally:
            # Clean up if we created a temporary file
            if asana_sample_path != "asana-openapi-sample.yaml" and os.path.exists(asana_sample_path):
                os.unlink(asana_sample_path)


if __name__ == '__main__':
    unittest.main()