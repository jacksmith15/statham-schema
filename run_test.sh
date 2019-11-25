#!/usr/bin/env bash

blue='\e[1;34m'
white='\e[0;37m'


header() {
    local header
    local len
    local width
    header="$1"
    len="${#header}"
    width="$(tput cols)"
    let block="($width-$len - 4)/2"
    echo -e "$blue"
    printf '=%.0s' $(eval "echo {1.."$((block))"}")
    printf '%s' "  $header  "
    printf '=%.0s' $(eval "echo {1.."$((block))"}")
    echo -e "$white"
}

show_help() {
    echo "Usage:"
    echo "  -l, --lint: Run the linter"
    echo "  -t, --type: Run the type checker"
    echo "  -u, --unit: Run the unit tests"
    echo "  -c, --clean: Clean generated files"
    echo "  -a, --all: Run all tests"
    echo "  -h, --help: Display this help message"
}

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -l|--lint)
    LINT=True
    shift # past argument
    ;;
    -t|--type)
    TYPE=True
    shift # past argument
    ;;
    -u|--unit)
    UNIT=True
    shift # past argument
    ;;
    -c|--clean)
    CLEAN=True
    shift # past argument
    ;;
    -a|--all)
    LINT=True
    TYPE=True
    UNIT=True
    shift # past argument
    ;;
    -h|--help)
    show_help
    exit 0
    ;;
    *)
    echo "Unknown argument $1"
    show_help
    exit 1
    ;;
esac
done


EXIT_CODE=0

if [[ -z ${COVERAGE_MIN_PERCENTAGE} ]];
then
    COVERAGE_MIN_PERCENTAGE=80
fi

clean() {
    header "Cleaning files"
    find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
    rm -rf cover || true
    rm -rf .coverage || true
    rm -f unit_test_results.xml || true
    rm -rf .pytest_cache || true
    rm -rf .mypy_cache || true
    rm -r build || true
    rm -r dist || true
    rm -r statham_schema.egg-info || true
}

lint() {
    header "Linting"
    PYLINT_CMD="pylint --output-format=colorized" 
    $PYLINT_CMD --rcfile statham/.pylintrc statham || EXIT_CODE=1 
    $PYLINT_CMD --rcfile tests/.pylintrc tests || EXIT_CODE=1
}

typecheck() {
    header "Checking types"
    mypy --ignore-missing-imports statham tests || EXIT_CODE=1
}

tests() {
    header "Running unit tests"
    pytest -v -s --junitxml=unit_test_results.xml --cov="statham" --cov-append --cov-branch --cov-report= tests || EXIT_CODE=1
}

coverage_check() {
    header "Checking coverage"
    coverage report --skip-covered --fail-under=${COVERAGE_MIN_PERCENTAGE:-0} || (echo Failed to meet minimum coverage of "$COVERAGE_MIN_PERCENTAGE"% && EXIT_CODE=1)

    coverage html -d "cover"
    coverage xml -o "cover/coverage.xml"
}

if [[ -n ${CLEAN} ]];
then
    clean
fi
if [[ -n ${LINT} ]];
then
    lint
fi
if [[ -n ${TYPE} ]];
then
    typecheck
fi
if [[ -n ${UNIT} ]];
then
    tests
    coverage_check
fi

exit $EXIT_CODE
