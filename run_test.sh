#!/usr/bin/env bash
ls

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
esac
done


EXIT_CODE=0

if [[ -z ${COVERAGE_MIN_PERCENTAGE} ]];
then
    COVERAGE_MIN_PERCENTAGE=80
fi

clean() {
    find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
    rm -rf cover
    rm -rf .coverage
    rm -f unit_test_results.xml
    rm -rf .pytest_cache
    rm -rf .mypy_cache
}

lint() {
    PYLINT_CMD="pylint --output-format=colorized" 
    $PYLINT_CMD --rcfile jsonschema_objects/.pylintrc jsonschema_objects || EXIT_CODE=1 
    $PYLINT_CMD --rcfile tests/.pylintrc tests || EXIT_CODE=1
}

typecheck() {
    mypy --ignore-missing-imports jsonschema_objects tests || EXIT_CODE=1
}

tests() {
    pytest -v -s --junitxml=unit_test_results.xml --cov="jsonschema_objects" --cov-append --cov-branch --cov-report= tests || EXIT_CODE=1
}

coverage_check() {
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
