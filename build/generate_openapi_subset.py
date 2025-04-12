#!/usr/bin/env python3
"""
Entry point for the console application.
"""
import sys
import os
import logging
import argparse
from openapi_operations import (
    load_openapi_spec,
    remove_descriptions,
    remove_extensions,
    output_openapi_spec_to_stdout
)


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Process an OpenAPI specification file."
    )
    parser.add_argument(
        "openapi_spec",
        help="Path to the OpenAPI specification file (JSON or YAML format)"
    )
    parser.add_argument(
        "--remove-descriptions",
        action="store_true",
        default=False,
        help="Remove description fields from the OpenAPI specification"
    )
    parser.add_argument(
        "--remove-extensions",
        action="store_true",
        default=False,
        help="Remove OpenAPI Extensions (properties starting with x-) from the specification"
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        default=False,
        help="Output the OpenAPI specification in YAML format instead of JSON"
    )
    
    args = parser.parse_args()
    
    # Return the parsed arguments
    return args


def main():
    """
    Main entry point for the application.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        logger = setup_logging()

        # Parse command line arguments
        args = parse_arguments()
        
        # Log the start of the application with the provided file name
        logger.debug(f"Application started with OpenAPI spec file: {args.openapi_spec}")
        
        # Validate that the file exists and is readable
        if not os.path.isfile(args.openapi_spec):
            logger.error(f"Error: The file '{args.openapi_spec}' does not exist.")
            return 1
        
        if not os.access(args.openapi_spec, os.R_OK):
            logger.error(f"Error: The file '{args.openapi_spec}' is not readable.")
            return 1

        logger.debug(f"Successfully validated OpenAPI spec file: {args.openapi_spec}")

        # Load the OpenAPI spec
        try:
            openapi_spec = load_openapi_spec(args.openapi_spec)

            # Remove descriptions if requested
            if args.remove_descriptions:
                logger.debug("Removing description fields from the OpenAPI spec")
                openapi_spec = remove_descriptions(openapi_spec)

            # Remove extensions if requested
            if args.remove_extensions:
                logger.debug("Removing extension fields from the OpenAPI spec")
                openapi_spec = remove_extensions(openapi_spec)

            # Output the OpenAPI spec to stdout in JSON format
            output_openapi_spec_to_stdout(openapi_spec, use_yaml=args.yaml)
        except Exception as e:
            logger.error(f"Error processing OpenAPI spec: {str(e)}", exc_info=True)
            return 1

        logger.debug("Application completed successfully")
        return 0
    except Exception as e:
        # If logger is not defined (e.g., setup_logging failed), use root logger
        try:
            logger.error(f"An error occurred: {e}", exc_info=True)
        except UnboundLocalError:
            # Fallback to root logger if logger is not defined
            logging.error(f"An error occurred during application startup: {e}", exc_info=True)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())