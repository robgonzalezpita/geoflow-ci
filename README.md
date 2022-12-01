# geoflow-ci
The top level utilities for handling automation of GeoFLOW.

The program ci_auto.py is designed to run on some of the HPC machines. As of November 2022, it is written to run on Hera, and is still being run manually. The configuration file CIrepos.cfg lists the github repositories that have their Pull Requests checked for labels that specify a machine, a compiler, and a test.

Call the test with: ./start_ci_py_pro.sh

The program ci_auto.py requires:

* ConfigParser module to read and write configuration files
* PyGithub module to use the github API

The test will look at pull requests, clone a repository, and run scripts to build the code. 

If the `ci-\<machine>-\<compiler>-build` label is applied to a Pull Request, the build test/s will run. 

If the `ci-\<machine>-\<compiler>-int` label is applied to a Pull Request, the build and integration test/s will run. 



### Example Crontab entry on HPC: 

```
5-59/15 * * * * cd /scratch2/BMC/gsd-hpcs/geoflow_ci/autoci/tests/auto && /bin/bash --login start_ci_py_pro.sh hera ci_auto.py >> ci_auto.out 2>&1

10-59/15 * * * * cd /scratch2/BMC/gsd-hpcs/geoflow_ci/autoci/tests/auto && /bin/bash --login start_ci_py_pro.sh hera ci_long.py >> ci_long.out 2>&1

15 11,23 * * * cd /scratch2/BMC/gsd-hpcs/geoflow_ci/autoci/tests/auto && /bin/bash --login log_clean.sh >/dev/null 2>&1
```