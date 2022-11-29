# geoflow-ci
The top level utilities for handling automation of GeoFLOW.

The program ci_auto.py is designed to run on some of the HPC machines. As of November 2022, it is written to run on Hera, and is still being run manually. The configuration file CIrepos.cfg lists the github repositories that have their Pull Requests checked for labels that specify a machine, a compiler, and a test.

Call the test with: ./start_ci_py_pro.sh

The program ci_auto.py requires:
* ConfigParser module to read and write configuration files
* PyGithub module to use the github API

The test will look at pull requests, clone code, and run scripts to build the code. If workflow is selected, the workflow will be run.
