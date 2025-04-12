"""
Conformance tests for the generate_openapi_subset application.
These tests verify that the application meets the functional requirement:
"Implement the entry point for The App."
"""
import unittest
import sys
import os
import subprocess
import importlib
from unittest.mock import patch
import logging
import tempfile
import io


class TestAppEntryPoint(unittest.TestCase):
    """Test cases to verify the entry point functionality of the application."""

    def setUp(self):
        """Set up test environment."""
        # Ensure the application file exists
        self.app_path = os.path.join(os.getcwd(), "generate_openapi_subset.py")
        # Create a temporary OpenAPI spec file for testing
        self.temp_file = self.create_temp_openapi_file()
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
            
    def create_temp_openapi_file(self):
        """Create a temporary OpenAPI spec file for testing."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        with os.fdopen(fd, 'w') as f:
            f.write('openapi: 3.0.0\ninfo:\n  title: Test API\n  version: 1.0.0')
        # Check that the application file exists
        self.assertTrue(os.path.exists(self.app_path), 
                        f"Application file not found at {self.app_path}")
        return path
        

    def test_basic_entry_point(self):
        """
        Test that the application has a proper entry point that returns success.
        This is the most basic test to verify the entry point exists and works.
        """
        # Mock sys.argv to provide the required command-line arguments
        original_argv = sys.argv
        sys.argv = ['generate_openapi_subset.py', self.temp_file]
        
        try:
            # Import the module
            import generate_openapi_subset
            # Reload to ensure it picks up the new sys.argv
            importlib.reload(generate_openapi_subset)
            
            result = generate_openapi_subset.main()
            
            # Verify it returns 0 (success)
            self.assertEqual(result, 0, 
                             "The main function should return 0 on successful execution")
        finally:
            # Restore original argv
            sys.argv = original_argv

    def test_command_line_execution(self):
        """
        Test that the application can be executed via command line.
        This verifies the application works when run as a script.
        """
        # Run the application as a subprocess
        result = subprocess.run([sys.executable, self.app_path, self.temp_file], 
                                capture_output=True, text=True)
        
        # Check return code
        self.assertEqual(result.returncode, 0, 
                         f"Application should exit with code 0, but got {result.returncode}. "
                         f"stdout: {result.stdout}, stderr: {result.stderr}")

    def test_logging_configuration(self):
        """
        Test that the application properly sets up logging.
        This verifies the logging functionality is properly initialized.
        """
        # Run the application as a subprocess and capture both stdout and stderr
        result = subprocess.run(
            [sys.executable, self.app_path, self.temp_file],
            capture_output=True,
            text=True
        )
        
        # Check that logs were captured in the combined output
        log_output = result.stdout + result.stderr
        self.assertIn("Application started", log_output, "Expected debug log 'Application started' not found in logs")
        self.assertIn("Application completed successfully", log_output, 
                      "Expected debug log 'Application completed successfully' not found in logs")

    def test_error_handling(self):
        """
        Test that the application handles errors gracefully.
        This verifies the error handling functionality of the entry point.
        """        
        # Set up sys.argv
        original_argv = sys.argv
        sys.argv = ['generate_openapi_subset.py', self.temp_file]
        
        try:
            # Import the module
            import generate_openapi_subset
            # Reload to ensure it picks up the new sys.argv
            importlib.reload(generate_openapi_subset)
            
            # Patch the setup_logging function to raise an exception
            with patch('generate_openapi_subset.setup_logging') as mock_setup:
                mock_setup.side_effect = Exception("Test exception")
                
                # Call the main function
                result = generate_openapi_subset.main()
                
                # Verify it returns non-zero (error)
                self.assertNotEqual(result, 0, 
                                   "The main function should return non-zero on error")
                self.assertEqual(result, 1, 
                                "The main function should return 1 on error")
        finally:
            # Restore original argv
            sys.argv = original_argv

    def test_module_import(self):
        """
        Test that the application can be imported as a module without executing main.
        This verifies the application has proper guards around the entry point.
        """
        # Remove the module if it's already imported
        if 'generate_openapi_subset' in sys.modules:
            del sys.modules['generate_openapi_subset']
        
        # Capture stdout to verify main() is not called
        with patch('sys.exit') as mock_exit:
            # Import the module
            importlib.import_module('generate_openapi_subset')
            
            # Verify sys.exit was not called (main was not executed)
            mock_exit.assert_not_called()


if __name__ == '__main__':
    unittest.main()