import subprocess
import os
import json


def validate_nc_file(filename: str):
    with open(os.path.dirname(__file__) + '/../settings.json', "r") as settings:
        data = json.load(settings)
        pnc_bin_path =  data['pnetcdf_bin_dir']
    ncvalidator  = os.path.join(pnc_bin_path, "ncvalidator")
    rc = subprocess.call([ncvalidator, '-q', filename],
                            stdout=subprocess.PIPE)
    return rc
    