## Notes for PnetCDF-python developers

This file contains instructions for PnetCDF-Python developers.
Users of PnetCDF-Python please refer to the
[PnetCDF-Python User Guide](https://pnetcdf-python.readthedocs.io/en/latest/).

* [Making A New Release](#making-a-new-release)
* [Library Packaging And Publishing](#library-packaging-and-publishing)

---
### Making A New Release

Below is a list of tasks to be done immediately before making a new release
(must run in the following order).

1. Update the release version string
   * Edit file [src/pnetcdf/__init__.py](src/pnetcdf/__init__.py) and change
     the following string.
     ```
     __version__ = "1.0.0"
     ```

2. Update release note
   * Edit file [RELEASE_NOTES.md](RELEASE_NOTES.md) to include notes about new
     features and other noticeable changes.
   * Update the release date.

3. Commit all changes to github repo
   * Run command below to upload changes to github.com.
   ```
   git push upstream main
   ```

4. Create a tag and push it to the gitbub repo
   * Run commands below to do so. Replace the proper version string.
   ```
   git tag -a v.1.0.0.pre -m "1.0.0 pre-release"
   git push upstream v.1.0.0.pre
   ```
5. On the browser, click [tags](https://github.com/Parallel-NetCDF/PnetCDF-Python/tags)
   * Click the name of tag just pushed.
   * Click "Create release from tag".
   * Fill in "Release title"
   * Fill in "Description field"
   * Optionally, click "Set as a pre-release", if this is a pre-release.
   * Optionally, click "Generate release notes", which will add a list of all
     PRs and new contributors into the Description field..
   * Click "Save draft" to save the changes. It can be modified later.
   * See all options from [github docs](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)

6. If a new commit were added or pushed to the main branch after a draft
   release was created, make sure the local main branch is up-to-date and then
   run commands below to force-update the tag on both local and remote.
   ```
   git tag -fa v.1.0.0.pre
   git push -f --tags
   ```

---
### Library Packaging And Publishing
 * Currently, pip-install via build distribution is disabled. No wheel files are uploaded to PyPI. Lastest pnetcdf-python package on PyPI: https://pypi.org/project/pnetcdf/
 * Packaging: build source distribution and wheel distribution on a local machine following the steps
   1. Make sure a python virtual env is created and install PnetCDF-C and all python dependencies as developer installation
      ```
      python -m venv env
      source env/bin/activate
      pip install --upgrade pip setuptools wheel packaging
      pip install numpy Cython
      CC=/path/to/mpicc pip install mpi4py
      ```
   2. Download the release tarball as shown in the following example
      ```
      wget https://github.com/Parallel-NetCDF/PnetCDF-Python/archive/refs/tags/v.1.0.0.pre.tar.gz
      tar -xfv v.1.0.0.pre.tar.gz
      cd PnetCDF-Python
      python3 -m pip install --upgrade build twine
      ```
   3. Build the package and generate distribution. 

      ```
      CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir python3 -m build
      ```
      A successful run of this command will generate 2 new files:  `dist/pnetcdf-x.x.x.tar.gz` and `dist/pnetcdf-x.x.x-cp39-cp39-linux_x86_64.whl`
      
 * For testing purpose: publish on [TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/). Only upload source distribution archive, since the wheel file (dist/pncpy-x.x.x*.whl) works exclusively for your own system and python version and not useful for users.
   1. Create TestPyPI account and update `$HOME/.pypirc` on local machine to skip cresendentials
   2. Publish source distribution on TestPyPI
       ```
       python3 -m twine upload --repository testpypi dist/pnetcdf-x.x.x.tar.gz
       ```
       The commmand will first check if there exists same package name and version number and error out if there exists. After uploading, open your browser, go to `https://test.pypi.org/` and search package name: `pnetcdf` to verify.
   3. Next we need to test the uploaded distribution on a local machine
      * Need to create a new empty folder. E.g. `mkdir pypi_test`
      * Create and activate a new vanilla python env for testing. Make sure PnetCDF-C and mpich are installed. This env shouldn't be the same env used in developer install. i.e. the enviroment does not contain any pre-installed pnetcdf python library
        ```
        python -m venv testenv
        source env/bin/activate
        ```
      * Then quick install via the distribution on TestPyPI (no python dependencies required). Note that `-i` redirects pip-install to search pnetcdf-python in testpypi index and `--extra-index-url` redirects pip-install to search dependency libraries (e.g. numpy) in official pypi index. 
       ```
       CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pnetcdf==x.x.x
       ```
       This command will download the package from testpypi and install pnetcdf library in the current env
   5. Run pnetcdf-python test programs. For example, using the test programs under `https://github.com/Parallel-NetCDF/PnetCDF-Python/tree/main/examples`

 * Officially publish on [PyPI](https://pypi.org/) WARNING: after upload to pypi, we cannot overwrite or change the published package!
   1. Create PyPI account and update `.pypirc` per instruction
   2. Publish source distribution on PyPI
       ```
       python3 -m twine upload dist/pnetcdf-x.x.x.tar.gz
       ```
   3. For testing, just create a new virtual env and quick install (using default PyPI index) without source code repo.
       ```
       CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install pnetcdf
       ```
   4. To verify the official publishing of latest pnetcdf verion, open the browser and go to `https://pypi.org/project/pnetcdf/` to check the latest release.


### Library installation
 * Quick install
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
   * More notes about quick install
     1. Source distribution(.tar.gz)
       * Pip-install command’s second go-to option if no matching build distribution is found on PyPI. It will build its own wheel file for the current system. For python libs with C-extension (like pnetcdf-python, netcdf4-python, h5py), wheel installation require their C bindings.
       * Invariant to platforms/versions, usually each version of python library has one single source distribution.
     2. Build distribution (.whl)
       * Pip-install command’s first go-to option by default. For python libs with C-extension (like pnetcdf-python, netcdf4-python, h5py), wheel installation does not require their C bindings.
       * Wheels are platform-specific and python-version specific. Different system used for building and uploading will generate different versions of wheel files on PyPI. To cover most mainstream python versions and operating systems, python libraries (like [numpy 1.25](https://pypi.org/project/numpy/#files)) has 20+ wheels files to cover most mainstream systems (e.g. Linux (x86_64), macOS (x86_64), and Windows (32-bit and 64-bit)) and recent python versions.
       * General procedures of  building and uploading python library wheels (build distributions) for MacOS and Linux systems
         * Python libs with C-extension (like pncpy, netcdf4-python, h5py) requires shared object (.so in linux and .dylibs in mac) files collected from C software installation. When making python library wheels (build distribution), an extra post-processing step (Delocate tool for Mac, auditwheel Tool in linux) is usually performed to copy and store these files in the python package to remove these dependencies. That’s why the user’s pip install with build distribution does not require a C installation as a prerequisite.
         * For MacOS wheels (like netCDF4-1.6.4-cp311-cp311-macosx_10_9_x86_64.whl), need to: Build the package to create the wheel -> Use Delocate tool to fix wheels -> Upload to PyPI.
         * For Linux wheels, need to: Pull manylinux docker image -> build the package to create the wheel in this container -> Use auditwheel Tool to fix wheels -> Upload to PyPI.
         * For some python libraries (numpy, netCDF4), a [dedicated github repo](https://github.com/MacPython/netcdf4-python-wheels) is used to automate building wheels for every release.


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
