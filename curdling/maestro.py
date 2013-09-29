from __future__ import absolute_import, unicode_literals, print_function
from collections import defaultdict
from distlib.util import parse_requirement
from distlib.version import LegacyMatcher

from . import util


def constraints(requirement):
    return (
        ','.join(' '.join(x) for x in requirement.constraints or ())
        or None)


class Maestro(object):

    def __init__(self):
        # This is the structure that saves all the meta-data about all the
        # requested packages. If you want to see how this structure looks like
        # when it contains actuall data.
        #
        # You should take a look in the file # `tests/unit/test_maestro.py`.
        # It contains all the possible combinations of values stored in this
        # structure.
        self.mapping = defaultdict(
            lambda: defaultdict(
                lambda: dict(dependency_of=[], data=None)))

        # The possible states of a package
        self.failed = set()
        self.retrieved = set()
        self.built = set()
        self.installed = set()

    def file_package(self, package, dependency_of=None):
        requirement = parse_requirement(package)
        version = constraints(requirement)
        entry = self.mapping[util.safe_name(requirement.name)][version]
        if dependency_of is not None:
            entry['dependency_of'].append(dependency_of)

    def get_data(self, package):
        requirement = parse_requirement(package)
        version = constraints(requirement)
        return self.mapping[util.safe_name(requirement.name)][version]['data']

    def set_data(self, package, data):
        pkg = parse_requirement(package)
        version = constraints(pkg)
        self.mapping[util.safe_name(pkg.name)][version]['data'] = data

    def mark(self, attr, package, data):
        pkg = parse_requirement(package)
        getattr(self, attr).add(util.safe_name(pkg.name))

        # The 'installed' label doesn't actually need to save any data, so we
        # just skip it. Going a little deeper, it's not possible cause we don't
        # actually have the version information when we are installing
        # packages. Needed to find the right bucket inside of the
        # project_name+version sub-dictionary structure.
        if data is not None:
            self.set_data(package, data)

    def best_version(self, package_name):
        versions = self.mapping[util.safe_name(package_name)].items()

        # We're looking for the version directly requested by the user. We
        # find it looking for versions that contain `None` in their field
        # `dependency_of`.
        for version, data in versions:
            if data['dependency_of'] is None:
                return version, data

        # The user didn't inform any specific version in the main requirements
        # (the ones received from the command line arguments, handled
        # above). This will be improved by fixing the issue #13.
        return versions[0]


    def should_queue(self, package):
        pkg = parse_requirement(package)
        return util.safe_name(pkg.name) not in self.mapping

    def pending(self, set_name):
        return list(set(self.mapping.keys())
            .difference(getattr(self, set_name))
            .difference(self.failed))
