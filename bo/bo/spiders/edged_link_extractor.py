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
from bo.utils.preconditions import check_not_none


class EdgedLinkExtractor(object):
    def __init__(self, inner_extractor, child_to_parent_map):
        self.inner_extractor = check_not_none(inner_extractor, 'inner_extractor')
        self.child_to_parent_map = check_not_none(child_to_parent_map, child_to_parent_map)

    def extract_links(self, response):
        all_links = self.inner_extractor.extract_links(response)
        parent = response.url
        for child in all_links:
            self.child_to_parent_map[child.url] = parent

        return all_links
