"""
Conformance tests for the OpenAPI subset generator application.
These tests verify that the application correctly handles command-line arguments
and file validation according to the functional requirements.
"""
import unittest
import subprocess
import os
import tempfile
import stat


class TestCommandLineArguments(unittest.TestCase):
    """Test cases for command-line argument handling."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file to use as a valid input
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.temp_file.write(b"openapi: 3.0.0\ninfo:\n  title: Test API\n  version: 1.0.0")
        self.temp_file.close()
        
        # Path to the main application script
        self.app_path = "generate_openapi_subset.py"
        
        # Ensure the application script exists
        self.assertTrue(os.path.exists(self.app_path), 
                        f"Application script {self.app_path} not found")

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_valid_single_argument(self):
        """Test that the application accepts a single valid file argument."""
        # Run the application with a valid file
        result = subprocess.run(
            ["python", self.app_path, self.temp_file.name],
            capture_output=True,
            text=True
        )
        
        # Check that the application exited successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with valid file argument. Output: {result.stderr}")

    def test_missing_argument(self):
        """Test that the application fails when no arguments are provided."""
        # Run the application with no arguments
        result = subprocess.run(
            ["python", self.app_path],
            capture_output=True,
            text=True
        )
        
        # Check that the application exited with an error
        self.assertNotEqual(result.returncode, 0, 
                           "Application should fail when no arguments are provided")
        
        # Check that the error message mentions arguments
        self.assertIn("argument", result.stderr.lower(), 
                     "Error message should mention missing argument")

    def test_too_many_arguments(self):
        """Test that the application fails when too many arguments are provided."""
        # Run the application with multiple arguments
        result = subprocess.run(
            ["python", self.app_path, self.temp_file.name, "extra_arg1", "extra_arg2"],
            capture_output=True,
            text=True
        )
        
        # Check that the application exited with an error
        self.assertNotEqual(result.returncode, 0, 
                           "Application should fail when too many arguments are provided")
        
        # Check that the error message mentions arguments
        self.assertIn("argument", result.stderr.lower(), 
                     "Error message should mention too many arguments")

    def test_nonexistent_file(self):
        """Test that the application validates file existence."""
        # Run the application with a non-existent file
        result = subprocess.run(
            ["python", self.app_path, "nonexistent_file.yaml"],
            capture_output=True,
            text=True
        )
        
        # Check that the application exited with an error
        self.assertEqual(result.returncode, 1, 
                        "Application should exit with code 1 when file doesn't exist")
        
        # Check that the error message mentions the file not existing
        self.assertIn("not exist", result.stderr.lower(), 
                     "Error message should mention that the file doesn't exist")

    def test_unreadable_file(self):
        """Test that the application validates file readability."""
        # Make the temporary file unreadable
        os.chmod(self.temp_file.name, 0)
        
        try:
            # Run the application with an unreadable file
            result = subprocess.run(
                ["python", self.app_path, self.temp_file.name],
                capture_output=True,
                text=True
            )
            
            # Check that the application exited with an error
            self.assertEqual(result.returncode, 1, 
                            "Application should exit with code 1 when file is not readable")
            
            # Check that the error message mentions the file not being readable
            self.assertIn("not readable", result.stderr.lower(), 
                         "Error message should mention that the file is not readable")
        finally:
            # Make the file readable again so it can be deleted in tearDown
            os.chmod(self.temp_file.name, stat.S_IRUSR | stat.S_IWUSR)


class TestWithSampleOpenAPISpec(unittest.TestCase):
    """Test cases using the sample OpenAPI specification."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file with the sample OpenAPI spec
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        
        # Sample content from the resource
        sample_content = """openapi: 3.0.0
info:
  description: >-
    This is the interface for interacting with the [Asana
    Platform](https://developers.asana.com).
  title: Asana
  version: '1.0'
paths: {}
components:
  schemas: {}
"""
        self.temp_file.write(sample_content.encode('utf-8'))
        self.temp_file.close()
        
        # Path to the main application script
        self.app_path = "generate_openapi_subset.py"

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_with_sample_spec(self):
        """Test that the application works with a sample OpenAPI spec."""
        # Run the application with the sample spec
        result = subprocess.run(
            ["python", self.app_path, self.temp_file.name],
            capture_output=True,
            text=True
        )
        
        # Check that the application exited successfully
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with sample OpenAPI spec. Output: {result.stderr}")


if __name__ == '__main__':
    unittest.main()