# stdlib
from subprocess import PIPE, Popen

# 3rd party
import pytest
from domdf_python_tools.paths import in_directory
from testing_tox import run_tox


@pytest.fixture()
def basic_testenv(tmp_pathplus):

	(tmp_pathplus / "tox.ini").write_lines([
			"[tox]",
			"isolated_build = True",
			"[testenv:demo]",
			"deps = dom_toml==0.4.0",
			"commands = python3 -m pip list",
			])

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = ["whey"]',
			'build-backend = "whey"',
			"[project]",
			'name = "minversions_demo"',
			'version = "1.2.3"',
			"dependencies = ['dom_toml>=0.3.0']",
			])

	(tmp_pathplus / "minversions_demo").mkdir()
	(tmp_pathplus / "minversions_demo" / "__init__.py").touch()

	return tmp_pathplus


def test_run_minversions_option(basic_testenv, tmp_pathplus, capsys):

	with (basic_testenv / "tox.ini").open('a') as fp:
		fp.write("minversions = true")

	try:
		run_tox(["-e", "demo", "-r"], tmp_pathplus)
	finally:
		stdout = capsys.readouterr().out
		print(stdout)

	assert "inst-nodeps:" in stdout
	assert "install-minversions: dom-toml==0.3.0" in stdout

	with in_directory(tmp_pathplus):
		tox_process = Popen([".tox/demo/bin/pip", "list"], stdout=PIPE, stderr=PIPE)

	stdout, stderr = tox_process.communicate()
	assert "dom-toml           0.3.0" in stdout.decode("UTF-8")

	tox_process.wait()


def test_run_minversions_arg(basic_testenv, tmp_pathplus, capsys):
	try:
		run_tox(["-e", "demo", "-r", "--minversions"], tmp_pathplus)
		# TODO: test with multiple envs
	finally:
		stdout = capsys.readouterr().out
		print(stdout)

	assert "inst-nodeps:" in stdout
	assert "install-minversions: dom-toml==0.3.0" in stdout

	with in_directory(tmp_pathplus):
		tox_process = Popen([".tox/demo/bin/pip", "list"], stdout=PIPE, stderr=PIPE)

	stdout, stderr = tox_process.communicate()
	assert "dom-toml           0.3.0" in stdout.decode("UTF-8")

	tox_process.wait()


def test_run_default(basic_testenv, tmp_pathplus, capsys):
	try:
		run_tox(["-e", "demo", "-r"], tmp_pathplus)
	finally:
		stdout = capsys.readouterr().out
		print(stdout)

	assert "inst-nodeps:" not in stdout
	assert "install-minversions:" not in stdout

	with in_directory(tmp_pathplus):
		tox_process = Popen([".tox/demo/bin/pip", "list"], stdout=PIPE, stderr=PIPE)

	stdout, stderr = tox_process.communicate()
	assert "dom-toml           0.4.0" in stdout.decode("UTF-8")

	tox_process.wait()


def test_run_minversions_arg_skipinstall(basic_testenv, tmp_pathplus, capsys):
	with (basic_testenv / "tox.ini").open('a') as fp:
		fp.write("skip_install = true")

	try:
		run_tox(["-e", "demo", "-r", "--minversions"], tmp_pathplus)
	finally:
		stdout = capsys.readouterr().out
		print(stdout)

	assert "inst-nodeps:" not in stdout
	assert "install-minversions: dom-toml==0.3.0" not in stdout

	with in_directory(tmp_pathplus):
		tox_process = Popen([".tox/demo/bin/pip", "list"], stdout=PIPE, stderr=PIPE)

	stdout, stderr = tox_process.communicate()
	assert "dom-toml           0.3.0" not in stdout.decode("UTF-8")

	tox_process.wait()
