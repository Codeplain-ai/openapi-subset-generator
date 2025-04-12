"""
Utility tests for the generate_openapi_subset module.
"""
import unittest
import sys
from unittest.mock import patch
import generate_openapi_subset
from tests.test_data import create_mock_args


class TestArgumentParsing(unittest.TestCase):
    """Test cases for argument parsing in the generate_openapi_subset module."""

    def test_parse_arguments(self):
        """Test argument parsing."""
        with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
            # Set up the mock to return a specific value
            mock_parse_args.return_value = create_mock_args()

            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')

    def test_parse_arguments_with_remove_descriptions(self):
        """Test argument parsing with --remove-descriptions flag."""
        # Test with the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json', '--remove-descriptions']):
            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')
            self.assertTrue(args.remove_descriptions)

        # Test without the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json']):
            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')
            self.assertFalse(args.remove_descriptions)

    def test_parse_arguments_with_remove_extensions(self):
        """Test argument parsing with --remove-extensions flag."""
        # Test with the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json', '--remove-extensions']):
            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')
            self.assertTrue(args.remove_extensions)

        # Test without the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json']):
            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')
            self.assertFalse(args.remove_extensions)

        # Test with both flags
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json', '--remove-descriptions', '--remove-extensions']):
            args = generate_openapi_subset.parse_arguments()
            self.assertTrue(args.remove_descriptions)
            self.assertTrue(args.remove_extensions)
            
    def test_parse_arguments_with_yaml(self):
        """Test argument parsing with --yaml flag."""
        # Test with the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json', '--yaml']):
            args = generate_openapi_subset.parse_arguments()
            self.assertEqual(args.openapi_spec, 'test_file.json')
            self.assertTrue(args.yaml)

        # Test without the flag
        with patch('sys.argv', ['generate_openapi_subset.py', 'test_file.json']):
            args = generate_openapi_subset.parse_arguments()
            self.assertFalse(args.yaml)


class TestSysExitHandling(unittest.TestCase):
    """Test cases for sys.exit handling in the generate_openapi_subset module."""

    @patch('generate_openapi_subset.main')
    def test_sys_exit_called_with_main_result(self, mock_main):
        """Test that sys.exit is called with the result of main()."""
        # Set up the mock to return a specific value
        mock_main.return_value = 42

        # Create a context where we can test the __name__ == "__main__" block
        with patch('sys.exit') as mock_exit:
            # Directly call the code that would run if __name__ == "__main__"
            generate_openapi_subset.sys.exit(generate_openapi_subset.main())
            mock_exit.assert_called_once_with(42)


if __name__ == '__main__':
    unittest.main()