import os
import sys
import subprocess
import glob
import shutil
import configparser
from setuptools import setup, Extension
from setuptools.dist import Distribution
import mpi4py
import json
from packaging import version

open_kwargs = {'encoding': 'utf-8'}

PnetCDF_dir = os.environ.get('PNETCDF_DIR')
pnc_config = None


try:
    if pnc_config is None:
        if PnetCDF_dir is not None:
            pnc_config = os.path.join(PnetCDF_dir, 'bin/pnetcdf-config')
        else:  # otherwise, just hope it's in the users PATH.
            pnc_config = 'pnetcdf-config'
    HAS_PNCCONFIG = subprocess.call([pnc_config, '--libs'],
                                     stdout=subprocess.PIPE) == 0
except OSError:
    HAS_PNCCONFIG = False

# read setup.cfg
if not HAS_PNCCONFIG:
    setup_cfg = 'setup.cfg'
    sys.stdout.write('reading from setup.cfg...\n')
    config = configparser.ConfigParser()
    config.read(setup_cfg)
    try:
        pnc_config = config.get("options", "pnetcdf_config")
        HAS_PNCCONFIG = subprocess.call([pnc_config, '--libs'],
                                        stdout=subprocess.PIPE) == 0
    except: # TODO:Specify what type of error 
        HAS_PNCCONFIG = False



if not HAS_PNCCONFIG:
    raise ValueError("Error: cannot find pnetcdf-config in PNETCDF_DIR, PATH or from setup.cfg. Abort.")


def get_str_from_pnc_config(pnc_config, option: str) -> str:
    res = subprocess.Popen([pnc_config, option],
                           stdout=subprocess.PIPE).communicate()[0]
    return res.decode().strip()


# get pnc version
pnc_ver = get_str_from_pnc_config(pnc_config, "--version")


def is_pnc_ver_valid(pnc_ver: str) -> bool:
    if pnc_ver.split()[0] != "PnetCDF":
        return False
    current_version = version.parse(pnc_ver.split()[1])
    target_version = version.parse("1.12.3")
    if current_version < target_version:
        return False
    return True


if not is_pnc_ver_valid(pnc_ver):
    print("Error: Invalid PnetCDF Version. Got:", pnc_ver, file=sys.stderr)
    exit(-1)

pnc_libdir = get_str_from_pnc_config(pnc_config, "--libdir")
pnc_includedir = get_str_from_pnc_config(pnc_config, "--includedir")

print("pnc_ver:", pnc_ver)
print("pnc_libdir:", pnc_libdir)
print("pnc_includedir:", pnc_includedir)

#Store pnetcdf bin directory to settings for tests
pnc_bindir = os.path.join(get_str_from_pnc_config(pnc_config, "--prefix"), 'bin/')
pnc_bin_dict = {"pnetcdf_bin_dir": pnc_bindir}
with open("settings.json", "w") as setting_json:
    json.dump(pnc_bin_dict, setting_json)

src_root = os.path.join('src', 'pncpy')


src_base_all = ["_File", "_Dimension", "_utils", "_Variable"]
src_all = [os.path.join(src_root, x) for x in src_base_all]
src_all_c = [x + ".c" for x in src_all]

for src_c in src_all_c:
    if os.path.exists(src_c):
        os.remove(src_c)

inc_dirs = [pnc_includedir]
lib_dirs = [pnc_libdir]

# Do not require numpy for just querying the package
# Taken from the h5py setup file.
if any('--' + opt in sys.argv for opt in Distribution.display_option_names +
        ['help-commands', 'help']) or sys.argv[1] == 'egg_info':
    pass
else:
    # append numpy include dir.
    import numpy
    inc_dirs.append(numpy.get_include())

inc_dirs.append(mpi4py.get_include())
libs = ["pnetcdf"]
runtime_lib_dirs = lib_dirs
print("inc_dirs:", inc_dirs)
print("lib_dirs:", lib_dirs)
print("libs:", libs)
print("runtime_lib_dirs:", runtime_lib_dirs)

DEFINE_MACROS = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]


ext_modules = [
    Extension("pncpy." + x,
              [os.path.join(src_root, x + ".pyx")],
              define_macros=DEFINE_MACROS,
              libraries=libs,
              library_dirs=lib_dirs,
              include_dirs=inc_dirs + ['include'],
              runtime_library_dirs=runtime_lib_dirs,
              extra_compile_args=['-Wno-unreachable-code-fallthrough',
                                  '-Wno-unused-function',
                                  '-Wno-unreachable-code']
              )
    for x in src_base_all
]

for e in ext_modules:
    e.cython_directives = {'language_level': "3"}


def extract_version(file_name):
    version = None
    with open(file_name) as fi:
        for line in fi:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version


setup(
    name="pncpy",  # need by GitHub dependency graph
    version=extract_version(os.path.join(src_root, "__init__.py")),
    ext_modules=ext_modules,
    packages=['pncpy'],
    package_dir = {'pncpy': 'src/pncpy'}
)
