from bo.utils.exceptions import ArgumentNoneError


def check_not_none(obj, variable_name, exception=ArgumentNoneError):
    if obj is None:
        raise exception("'{0}' variable is None, when it shouldn't be.".format(variable_name))
    return obj


def check_not_none_or_whitespace(string, variable_name, exception=ValueError):
    if string is None or string.strip() == '':
        raise exception("'{0} variable is None or is whitespace, when it shouldn't be.".format(variable_name))
    return string
