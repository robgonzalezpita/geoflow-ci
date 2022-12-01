#!/bin/bash
set -eu

find /scratch2/BMC/gsd-hpcs/geoflow_ci/autoci/tests/auto -type f -name "*.log" -size -400c -delete
find /scratch2/BMC/gsd-hpcs/geoflow_ci/autoci/tests/auto -type f -name "*.log" -mtime +7 -delete

