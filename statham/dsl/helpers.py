import inspect


def custom_repr(self):
    """Dynamically construct the repr to match value instantiation."""
    param_strings = []
    parameters = list(
        inspect.signature(type(self).__init__).parameters.values()
    )[1:]
    for param in parameters:
        value = getattr(self, param.name, None)
        if value == param.default:
            continue
        if param.kind == param.VAR_POSITIONAL:
            param_strings.extend([repr(sub_val) for sub_val in value])
        elif param.kind == param.KEYWORD_ONLY:
            param_strings.append(f"{param.name}={repr(value)}")
        else:
            param_strings.append(repr(value))
    param_string = ", ".join(param_strings)
    return f"{type(self).__name__}({param_string})"
