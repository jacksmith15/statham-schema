"""Serializers for in-memory Element trees.

Elements may be serialized to a JSON dictionary or a Python module.
"""
from statham.serializers.python import serialize_python
from statham.serializers.json import serialize_json
