#!/usr/bin/env python3
#
#  __init__.py
"""
tox plugin which installs the *minimum* versions of a project's dependencies.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Parts based on https://github.com/tox-dev/tox/blob/master/src/tox/venv.py
#  MIT Licensed
#

# stdlib
import re
import tarfile
from types import MethodType
from typing import List, Optional, Tuple

# 3rd party
import tox  # type: ignore
import tox.reporter  # type: ignore
from cawdrey.header_mapping import HeaderMapping
from domdf_python_tools.stringlist import DelimitedList
from domdf_python_tools.utils import divide
from first import first
from packaging.requirements import Requirement
from packaging.specifiers import Specifier, SpecifierSet
from shippinglabel.requirements import marker_environment
from tox.action import Action  # type: ignore
from tox.config import Parser, TestenvConfig  # type: ignore
from tox.venv import VirtualEnv  # type: ignore

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["loads", "tox_addoption", "tox_runtest_pre", "tox_testenv_install_deps"]

WSP = " \t"

INVALID_OPS = {"<=", "!=", '<', '>'}
PINNED_OPS = {"==", "==="}
ALLOWED_OPS = {">=", "~="}


@tox.hookimpl
def tox_addoption(parser: Parser):  # noqa: D103
	parser.add_argument(
			"--minversions",
			action="store_true",
			default=False,
			help="Use the minimum versions of the project's dependencies for all environments",
			)
	parser.add_testenv_attribute(
			name="minversions",
			type="bool",
			default=False,
			help="Use the minimum versions of the project's dependencies for this environment",
			)


@tox.hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> Optional[bool]:
	"""
	Install the dependencies for the current environment.

	:param venv:
	:param action:
	"""

	envconfig: TestenvConfig = venv.envconfig

	if envconfig.skip_install:
		return None

	if "--minversions" in envconfig.config.args or envconfig.minversions:
		# envconfig.skip_install = True
		venv.install_pkg = MethodType(install_pkg, venv)

	return None


def install_pkg(  # noqa: D103
		self: VirtualEnv,
		dir,  # noqa: A002  # pylint: disable=redefined-builtin
		action: Action,
		name: str,
		is_develop: bool = False,
		):
	assert action is not None

	pip_flags = []

	if getattr(self, "just_created", False):
		self.finish()
		pip_flags.extend(["--exists-action", 'w'])
	else:
		if is_develop and not self._needs_reinstall(dir, action):
			action.setactivity(f"{name}-noop", dir)
			return

	action.setactivity(f"{name}-nodeps", dir)
	pip_flags.extend(["--no-deps"] + ([] if is_develop else ["-U"]))
	pip_flags.extend(["-v"] * min(3, tox.reporter.verbosity() - 2))

	if self.envconfig.extras:
		dir += "[{}]".format(','.join(self.envconfig.extras))
	target = [dir]
	if is_develop:
		target.insert(0, "-e")
	self._install(target, extraopts=pip_flags, action=action)


@tox.hookimpl
def tox_runtest_pre(venv: VirtualEnv):  # noqa: D103
	envconfig: TestenvConfig = venv.envconfig

	if envconfig.skip_install:
		return None

	if "--minversions" in envconfig.config.args or envconfig.minversions:
		extras = venv.envconfig.extras

		with tarfile.open(venv.envconfig.setenv["TOX_PACKAGE"], mode="r:gz") as fp:
			pkginfo_name = first(fp.getnames(), key=lambda n: n.endswith("PKG-INFO"))

			if pkginfo_name is None:
				raise FileNotFoundError("'PKG-INFO' file not found in the package.")

			metadata, description = loads(fp.extractfile(pkginfo_name).read().decode("UTF-8"))  # type: ignore

			provided_extras = metadata.get_all("Provides-Extra", default=[])

			for extra in extras:
				if extra not in provided_extras:
					tox.reporter.warning(f"The project does not provide the extra '{extra}'")

			requirements = []
			for requirement in map(Requirement, metadata.get_all("Requires-Dist", default=[])):
				if requirement.marker and not requirement.marker.evaluate(marker_environment(extras)):
					continue

				spec_operators = {s.operator for s in requirement.specifier}

				if all(s in PINNED_OPS for s in spec_operators):
					# All pinned exactly
					pass
				elif all(s in INVALID_OPS for s in spec_operators):
					tox.reporter.warning(f"Cannot determine minimum version for {requirement}")
				else:
					specifier = DelimitedList(
							Specifier(f"=={s.version}") for s in requirement.specifier if s.operator in ALLOWED_OPS
							)
					requirement.specifier = SpecifierSet(f"{specifier:,}")

				requirements.append(requirement)

			if requirements:
				deps = list(map(str, requirements))
				with venv.new_action("install-minversions") as action:
					action.setactivity("install-minversions", ','.join(deps))
					venv._install(deps, action=action)
			else:
				# TODO: link to issue
				tox.reporter.error(
						"No requirements to install. "
						"Your build backend may not be including the 'Requires-Dist' field in the PKG-INFO file.",
						)


def loads(rawtext: str) -> Tuple[HeaderMapping, str]:
	"""
	Parse Python core metadata from the given string.

	:param rawtext:

	:returns: A mapping of the metadata fields, and the long description
	"""

	try:
		rawtext, body = rawtext.split("\n\n", maxsplit=1)
	except ValueError:
		body = ''

	# unfold per RFC 5322 § 2.2.3
	rawtext = re.sub(rf"\n([{WSP}])", r"\1", rawtext)

	file_content: List[str] = rawtext.split('\n')
	file_content.reverse()

	fields: HeaderMapping[str] = HeaderMapping()

	while file_content:
		line = file_content.pop()

		if not line:
			break

		field_name, field_value = divide(line, ':')
		fields[field_name] = field_value.lstrip()

	return fields, body
