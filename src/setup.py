#
#   Copyright 2020 The Cloudforet Authors.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from setuptools import setup, find_packages

with open("VERSION", "r") as f:
    VERSION = f.read().strip()
    f.close()

setup(
    name="plugin-jira-inven-collector",
    version=VERSION,
    description="Collector plugin for Jira Software",
    long_description="",
    url="https://github.com/forest-extension/plugin-jira-software-inven-collector",
    author="Forest-Extension Admin",
    author_email="iam.minhokim@gmail.com",
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=["spaceone-api", "spaceone-inventory"],
    package_data={"plugin": ["metadata/*/*.yaml", "metrics/*/*/*.yaml"]},
    zip_safe=False,
)
