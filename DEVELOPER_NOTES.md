## Notes for PnetCDF-python developers
---
### Note on python library packaging
 * Quick install
   * Currently, quick install via `pip install pnetcdf` is disabled. Main challenge is that build distribution (using wheels) is platform-specific and multiple wheels need to be generated to cover all mainstream platforms. A working source distribution for `pip install` is easier and has been tested on PyPI (works for all platforms but still needs MPI and PnetCDF-C installation) 
   * `MANIFEST.in` controls files to be included in source distribution (sdist), which will be eventually uploaded to PyPI if we enables quick install in the future. After modifications to `MANIFEST.IN` file, here are steps to check if the files included are valid to build the library.
     1. Make sure pnetcdf.egg-info folder is deleted. Otherwise it will first cache previous versions of `MANIFEST.IN` requirement.
     2. Build the source distribution
     ```
     CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir python setup.py sdist
     ```
     3. Check source distribution content if the list matches `MANIFEST.IN`
     ```
     tar -tzf dist/package-<version>.tar.gz
     ```
     4. Install the library from sdist
     ```
     CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install dist/package-<version>.tar.gz
     ```
     5. Check installation by test and example programs
  * Developer install
    * Developer installation is mainly managed by `setup.py` and `pyproject.toml`. The former one is the core file to build the package and the latter manages dependencies required by `pip install` command.
    * `python setup.py install` builds and installs the python library based on the current python environment and will error out if dependency (e.g. mpi4py) not met. This command is going to be deprecated and is not recommended for modern python library installation.
    * `pip install .` works as a wrapper command for the above but it goes further: it automatically handles and install any dependencies listed in `pyproject.toml` file.Need to pay special attention to the dependencies listed in `requires` under `[build-system]` and `dependencies`. 
      * `dependencies` defines python libraries required for running the project and will first check if requirement already satisfied in current environment before installing the latest qualified version of the library.
      * `requires` defines libraries required for building the project. `pip install` by default creates and uses isolated building env for building stage which completely ignores current user env. For example, if user already installed mpi4py==3.1.6, "mpi4py>=3.1.4" will still automatically install a mpi4py 4.0.0 in the building env and thereafter use syntax from 4.0.0 to build pnetcdf-python. This caused version mismatch issues between building and running envs when numpy 2.0 and mpi4py 4.0.0 are released. To address this issue, current user guide forces to use current python env for building stage by adding ` -no-build-isolation` arg to `pip install` command.

### Note on configuring Read the Docs tool for user guide generation
 * Read the Docs settings
   * User guide is automatically generated on main branch changes and opened PR requests. Modify this in Read the Docs dashboard if needed
 * Doc files
   * `.readthedocs.yaml` -- The script that controls commands that run before installation of pnetcdf-python (under `pre-install:`) and installation (under `python:`)
   * `/docs/requirements.txt` -- Python dependencies required for doc generation, including `sphinx`
 * Important environment variables
   * User guide generation requires environment variables set by Read the Docs dashboard (`Admin` -> `Environment Variables`). Delete and add a new variable to modify (remember to select `Expose this environment variable in PR builds` if PR auto-build is enabled)
   * Current environment variables set (only effective solution found to set env variable at installation):
     * `CC`: mpicc.mpich
     * `PNETCDF_DIR`: /home/docs/checkouts/readthedocs.org/user_builds/pnetcdf-python/checkouts/latest/_readthedocs/PnetCDF
     * `PNETCDF_VER`: 1.12.3