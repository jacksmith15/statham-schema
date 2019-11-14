#!/usr/bin/env bash


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
    -a|--all)
    LINT=True
    TYPE=True
    UNIT=True
    shift # past argument
    ;;
esac
done


EXIT_CODE=0


lint() {
    PYLINT_CMD="pylint --output-format=colorized" 
    $PYLINT_CMD --rcfile jsonschema_objects/.pylintrc jsonschema_objects || EXIT_CODE=1 
    $PYLINT_CMD --rcfile tests/.pylintrc tests || EXIT_CODE=1
}

typecheck() {
    mypy jsonschema_objects tests || EXIT_CODE=1
}

tests() {
    pytest -s -v tests || EXIT_CODE=1
}

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
fi

exit $EXIT_CODE
