#
# Copyright (C) 2024, Northwestern University and Argonne National Laboratory
# See COPYRIGHT notice in top-level directory.
#

import subprocess
import os
import json


def validate_nc_file(pnc_dir: str, filename: str):
    ncvalidator  = os.path.join(pnc_dir, 'bin', "ncvalidator")
    rc = subprocess.call([ncvalidator, '-q', filename],
                            stdout=subprocess.PIPE)
    return rc
    
