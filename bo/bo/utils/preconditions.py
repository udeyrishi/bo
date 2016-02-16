"""
Copyright 2016 Udey Rishi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from bo.utils.exceptions import ArgumentNoneError


def check_not_none(obj, variable_name, exception=ArgumentNoneError):
    if obj is None:
        raise exception("'{0}' variable is None, when it shouldn't be.".format(variable_name))
    return obj


def check_not_none_or_whitespace(string, variable_name, exception=ValueError):
    if string is None or string.strip() == '':
        raise exception("'{0} variable is None or is whitespace, when it shouldn't be.".format(variable_name))
    return string
