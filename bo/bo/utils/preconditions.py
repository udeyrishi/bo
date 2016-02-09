from bo.utils.exceptions import ArgumentNoneError


def check_not_none(obj, variable_name, exception=ArgumentNoneError):
    if obj is None:
        raise exception("'{0}' variable is None, when it shouldn't be,".format(variable_name))
