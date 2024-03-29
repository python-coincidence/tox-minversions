================
tox-minversions
================

.. start short_desc

**tox plugin which installs the *minimum* versions of a project's dependencies**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Tests
	  - |actions_linux| |coveralls|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |actions_linux| image:: https://github.com/python-coincidence/tox-minversions/workflows/Linux/badge.svg
	:target: https://github.com/python-coincidence/tox-minversions/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_flake8| image:: https://github.com/python-coincidence/tox-minversions/workflows/Flake8/badge.svg
	:target: https://github.com/python-coincidence/tox-minversions/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/python-coincidence/tox-minversions/workflows/mypy/badge.svg
	:target: https://github.com/python-coincidence/tox-minversions/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/python-coincidence/tox-minversions/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/python-coincidence/tox-minversions/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/python-coincidence/tox-minversions/master?logo=coveralls
	:target: https://coveralls.io/github/python-coincidence/tox-minversions?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/python-coincidence/tox-minversions?logo=codefactor
	:target: https://www.codefactor.io/repository/github/python-coincidence/tox-minversions
	:alt: CodeFactor Grade

.. |license| image:: https://img.shields.io/github/license/python-coincidence/tox-minversions
	:target: https://github.com/python-coincidence/tox-minversions/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/python-coincidence/tox-minversions
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/python-coincidence/tox-minversions/v0.0.0
	:target: https://github.com/python-coincidence/tox-minversions/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/python-coincidence/tox-minversions
	:target: https://github.com/python-coincidence/tox-minversions/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2023
	:alt: Maintenance

.. end shields

Installation
--------------

.. start installation

``tox-minversions`` can be installed from GitHub.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install git+https://github.com/python-coincidence/tox-minversions

.. end installation

Usage
-------

Individual ``testenv``\s can be configured to use the minimum versions of dependencies by setting ``minversions = True`` like so:

.. code-block:: ini

	[testenv]
	minversions = True

Alternatively, the ``--minversions`` option can be given on the command line to use the minimum versions for *all* testenvs:

.. code-block:: bash

	$ tox --minversions
	$ tox -e py36,py37,mypy --minversions
