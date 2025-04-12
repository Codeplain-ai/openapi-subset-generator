#!/bin/bash

# Initialize VERBOSE to 0
VERBOSE=0
RENDER_RANGE=""

# Function to display usage
usage() {
  echo "Usage: $0 [-v|--verbose] [--render-range RENDER_RANGE] [-h|--help]"
  exit 1
}

# Parse flags and arguments
while [[ "$1" != "" ]]; do
  case $1 in
    -v | --verbose )
      VERBOSE=1
      echo "Running plain2code in verbose mode."
      ;;
    --render-range )
      shift
      RENDER_RANGE=$1
      ;;
    -h | --help )
      usage
      ;;
    -* )
      echo "Unknown option: $1"
      usage
      ;;
  esac
  shift
done

if [ "$VERBOSE" -eq 1 ]; then
    echo "Rendering..."
fi


# Check if PLAIN2CODE_RENDERER variable is set
if [ -z "${PLAIN2CODE_RENDERER_DIR:-}" ]; then
    echo "Error: PLAIN2CODE_RENDERER_DIR variable is not set. Please set the PLAIN2CODE_RENDERER_DIR variable to the directory containing the plain2code.py script."
    exit 1
fi

if [ -z "$RENDER_RANGE" ]; then
    # Removing all the conformance tests before rendering the hello world example.
    rm -rf conformance_tests
fi

python $PLAIN2CODE_RENDERER_DIR/plain2code.py openapi-subset-generator.plain --unittests-script=$PLAIN2CODE_RENDERER_DIR/test_scripts/run_unittests_python.sh --conformance-tests-script=$PLAIN2CODE_RENDERER_DIR/test_scripts/run_conformance_tests_python.sh --debug ${VERBOSE:+-v} ${RENDER_RANGE:+--render-range $RENDER_RANGE}
