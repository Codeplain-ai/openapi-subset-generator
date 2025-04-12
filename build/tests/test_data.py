"""
Test data and fixtures for OpenAPI subset generator tests.
"""
import json
import yaml
from unittest.mock import Mock

# Test OpenAPI specifications
VALID_OPENAPI_SPEC = {
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
                "responses": {
                    "x-response-type": "standard",
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object", 
                                    "properties": {
                                        "x-field-meta": {"internal": True},
                                        "id": { 
                                            "type": "string",
                                            "description": "The ID of the resource"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

OPENAPI_SPEC_WITHOUT_DESCRIPTIONS = {
    "openapi": "3.0.0",
    "info": {
        "title": "Test API", 
        "version": "1.0.0",
        "x-logo": {"url": "https://example.com/logo.png"}
    },
    "paths": {
        "/test": {
            "get": {
                "summary": "Test endpoint",
                "responses": {
                    "x-response-type": "standard",
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "x-field-meta": {"internal": True},
                                        "id": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

OPENAPI_SPEC_WITHOUT_EXTENSIONS = {
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
                "description": "This is a test endpoint",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "The ID of the resource"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# Mock data generators
def get_json_content():
    """Return a JSON string of the test OpenAPI spec."""
    return json.dumps(VALID_OPENAPI_SPEC)

def get_yaml_content():
    """Return a YAML string of the test OpenAPI spec."""
    return yaml.dump(VALID_OPENAPI_SPEC)

def get_invalid_content():
    """Return an invalid JSON/YAML string."""
    return "This is not valid JSON or YAML"

# Mock argument objects
def create_mock_args(filename='test_file.json', remove_descriptions=False, remove_extensions=False, yaml=False):
    """Create a mock args object for testing."""
    return Mock(openapi_spec=filename, remove_descriptions=remove_descriptions, remove_extensions=remove_extensions, yaml=yaml)