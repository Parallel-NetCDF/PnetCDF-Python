## Notes for PnetCDF-Python developers

This file contains instructions for PnetCDF-Python developers.

PnetCDF-Python users please refer to the
[PnetCDF-Python User Guide](https://pnetcdf-python.readthedocs.io/en/latest/).

* [Making A New Release](#making-a-new-release)
* [Library Packaging And Publishing](#library-packaging-and-publishing)
* [Library installation](#library-installation)
* [User Guide](#user-guide)

---
### Making A New Release

Below is a list of tasks to be done immediately before making a new release
(must run in the following order).

1. Update the release version string
   * Edit file [src/pnetcdf/__init__.py](src/pnetcdf/__init__.py) and update
     the following string to the new version number.
     ```
     __version__ = "1.0.0"
     ```
   <ul>
   <li> <details>
   <summary>GNU guideline for updating version numbers(click to expand)</summary>
   <li> For libtool Application Binary Versioning (ABI) versioning rules see:
      http://www.gnu.org/software/libtool/manual/libtool.html#Updating-version-info
   </li>
   <li> Update the version information only immediately before a public release.
   </li>
   <li> Quote from the GNU guide: Here are a set of rules to help you update
        your library version information:
     <ul>
     <li> Start with version information of '0:0:0' for each libtool library.
     </li>
     <li> Update the version information only immediately before a public
          release of your software. More frequent updates are unnecessary, and
          only guarantee that the current interface number gets larger faster.
     </li>
     <li> If the library source code has changed at all since the last update,
          then increment revision ('c:r:a' becomes 'c:r+1:a').
     </li>
     <li> If any interfaces have been added, removed, or changed since the last
          update, increment current, and set revision to 0.
     </li>
     <li> If any interfaces have been added since the last public release, then
          increment age.
     </li>
     <li> If any interfaces have been removed or changed since the last public
          release, then set age to 0.
     </li>
   </li>
   <ul>
   </details></li>
   </ul>


2. Update release note
   * Edit file [./RELEASE_NOTES.md](./RELEASE_NOTES.md) to include notes about
     new features and other noticeable changes.
   * Edit and update the release date.

3. Commit all changes to github repo
   * Run command below to upload changes to github.com.
   ```
   git push upstream main
   ```

4. Create a tag and push it to the github repo
   * Run commands below to do so. Replace the proper version string.
   ```
   git tag -a pnetcdf-python.1.0.0 -m "PnetCDF-Python package version 1.0.0"
   git push upstream pnetcdf-python.1.0.0
   ```

5. Create a new release from the tag on github.com.
   * Visit PnetCDF-Python github repo's
     [tags](https://github.com/Parallel-NetCDF/PnetCDF-Python/tags)
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
   git tag -fa pnetcdf-python.1.0.0
   git push -f --tags
   ```

---
### Library Packaging And Publishing
 * Currently, pip-install via build distribution is disabled. No wheel files
   are uploaded to PyPI. Lastest PnetCDF-Python package on PyPI can be found
   in: https://pypi.org/project/pnetcdf/
 * Packaging: build source distribution and wheel distribution on a local
   machine by following these steps.
   1. Install PnetCDF-C library
   2. Make sure a python virtual env is created and all python dependencies are
      installed as the developer installation.
      ```
      cd $HOME
      python -m venv tmp_env
      source $HOME/tmp_env/bin/activate
      pip install --upgrade pip setuptools wheel packaging
      pip install numpy Cython
      CC=/path/to/mpicc pip install mpi4py
      ```
   3. Download the release tarball of PnetCDF-Python. For example, use commands
      as shown below.
      ```
      wget https://github.com/Parallel-NetCDF/PnetCDF-Python/archive/refs/tags/pnetcdf-python.1.0.0.tar.gz
      tar -xfv pnetcdf-python.1.0.0.tar.gz
      cd PnetCDF-Python
      python3 -m pip install --upgrade build twine
      ```
   4. Build the package and generate distribution.
      ```
      CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir python3 -m build
      ```
      A successful run of this command will generate 2 new files:
      + `dist/pnetcdf-x.x.x.tar.gz` and
      + `dist/pnetcdf-x.x.x-cp39-cp39-linux_x86_64.whl`
   5. Leave the python environment, tmp_env, by running command
      ```
      deactivate
      ```

 * Test distribution
   1. For testing purpose, we must publish the package built above on
      [TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi),
      by only uploading source distribution archive, since the wheel file
      (dist/pnetcdf-x.x.x*.whl) works exclusively for your own system and python
      version and is not useful for the users.
   2. Create TestPyPI account.
      * Optionally, update file `$HOME/.pypirc` on local machine to skip
        the log-in credentials
   3. Publish source distribution on TestPyPI:
      ```
      python3 -m twine upload --repository testpypi dist/pnetcdf-x.x.x.tar.gz
      ```
      The command will first check if the same name and version number have
      already existed. The command will error out if the same names have been
      found. After uploading, open your browser, go to https://test.pypi.org
      and search for package name: `pnetcdf` to verify.
   4. Next, test the uploaded distribution on a local machine
      * Create a new empty folder. E.g.
        ```
        mkdir pypi_test
        cd pypi_test
        ```
      * Make sure PnetCDF-C and mpich are installed.
      * Create and activate a new vanilla python env for testing.
      * This env shouldn't be the same env used in developer install, i.e. the
        environment does not contain any pre-installed PnetCDF-Python library
        ```
        python -m venv test_env
        source test_env/bin/activate
        ```
      * Do a quick install via the distribution on TestPyPI (no python
        dependencies required). Note that `-i` redirects pip-install to search
        PnetCDF-Python in testpypi index and `--extra-index-url` redirects
        pip-install to search dependency libraries (e.g. numpy) in official
        pypi index.
        ```
        CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir \
        pip install -i https://test.pypi.org/simple/ \
                    --extra-index-url https://pypi.org/simple pnetcdf==x.x.x
        ```
        This command will download the package from testpypi and install
        PnetCDF-Python library in the current env.
   5. Run PnetCDF-Python test programs. For example, using test programs
      available in folder `test` of PnetCD-Python package.
      ```
      wget https://github.com/Parallel-NetCDF/PnetCDF-Python/archive/refs/tags/pnetcdf-python.1.0.0.tar.gz
      tar -xfv pnetcdf.1.0.0.tar.gz
      cd PnetCDF-Python
      cd test
      make check
      make ptests
      ```
      Test programs available in folder `examples`, which requires pytorch.
      ```
      cd ../examples
      pip install torch torchvision
      make check
      make ptests
      ```
      Leave the python environment, test_env, by running command
      ```
      deactivate
      ```

 * Publish official release on PyPI
   1. Official releases are published on [PyPI](https://pypi.org/)
   2. WARNING: after upload to pypi, one cannot overwrite or change the
      published package on pypi!
   3. Create PyPI account and update `.pypirc` per instructions above.
   4. Publish source distribution on PyPI
      ```
      python3 -m twine upload dist/pnetcdf-x.x.x.tar.gz
      ```
   5. For testing, just create a new virtual env and quick install (using
      default PyPI index) without source code repo.
      ```
      CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir pip install pnetcdf
      ```
   6. To verify the official published verion, open the browser and go to
      https://pypi.org/project/pnetcdf/ to check the latest release.


---
### Library installation
 * Quick install
   * `MANIFEST.in` controls files to be included in source distribution
     (sdist), which will be eventually uploaded to PyPI if we enables quick
     install in the future. After modifications to `MANIFEST.IN` file, here are
     steps to check if the files included are valid to build the library.
     1. Make sure pnetcdf.egg-info folder is deleted. Otherwise it will first
        cache previous versions of `MANIFEST.IN` requirement. This can be done
        by running command below at the root folder.
        ```
        make build-clean
        ```
     2. Build the source distribution
        ```
        CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir \
        python setup.py sdist
        ```
     3. Check source distribution content if the list matches `MANIFEST.IN`
        ```
        tar -tzf dist/package-<version>.tar.gz
        ```
     4. Install the library from sdist
        ```
        CC=/path/to/mpicc PNETCDF_DIR=/path/to/pnetcdf/dir \
        pip install dist/package-<version>.tar.gz
        ```
     5. Check installation by testing programs in folders test and examples

   * Additional notes about quick install
     1. Source distribution(.tar.gz)
        * Pip-install command’s second go-to option if no matching build
          distribution is found on PyPI. It will build its own wheel file for
          the current system. For python libs with C-extension (like
          PnetCDF-Python netcdf4-python, h5py), wheel installation require
          their C bindings.
        * Invariant to platforms/versions, usually each version of python
          library has one single source distribution.
     2. Build distribution (.whl)
        * Pip-install command’s first go-to option by default. For python libs
          with C-extension (like PnetCDF-Python netcdf4-python, h5py), wheel
          installation does not require their C bindings.
        * Wheels are platform-specific and python-version specific. Different
          system used for building and uploading will generate different
          versions of wheel files on PyPI. To cover most mainstream python
          versions and operating systems, python libraries (like
          [numpy 1.25](https://pypi.org/project/numpy/#files)) has 20+ wheels
          files to cover most mainstream systems (e.g. Linux (x86_64), MacOS
          (x86_64), and Windows (32-bit and 64-bit)) and recent python versions.
        * General procedures of building and uploading python library wheels
          (build distributions) for MacOS and Linux systems
          + Python libs with C-extension (like PnetCDF-Python, netcdf4-python,
            h5py) requires shared object (.so in Linux and .dylibs in mac)
            files collected from C software installation. When making python
            library wheels (build distribution), an extra post-processing step
            (Delocate tool for Mac, auditwheel Tool in linux) is usually
            performed to copy and store these files in the python package to
            remove these dependencies. That’s why the user’s pip install with
            build distribution does not require a C installation as a
            prerequisite.
          + For MacOS wheels (such as
            netCDF4-1.6.4-cp311-cp311-macosx_10_9_x86_64.whl) do the
            followings.
            1. Build the package to create the wheel,
            2. Use Delocate tool to fix wheels
            3. Upload to PyPI.
          + For Linux wheels, do the followings.
            1. Pull manylinux docker image
            2. Build the package to create the wheel in this container
            3. Use auditwheel Tool to fix wheels
            4. Upload to PyPI.
          + For some python libraries (numpy, netCDF4), a
            [dedicated github repo](https://github.com/MacPython/netcdf4-python-wheels)
            is used to automate building wheels for every release.


  * Developer install on a local machine
    * Developer installation is mainly managed by files `setup.py` and
      `pyproject.toml`. The former is the core file to build the package
      and the latter manages dependencies required by `pip install` command.
    * Command below builds and installs the python library based on the current
      python environment.
      ```
      python setup.py install
      ```
      The command will error out if any dependency (e.g. mpi4py) is missing.
      This command will soon be deprecated and is not recommended for modern
      python library installation.
    * Command below works as a wrapper command for the above but does further
      to automatically handle and install any dependencies listed in file
      `pyproject.toml`. Need to pay special attention to the dependencies
      listed in the filed of `requires` under `[build-system]` and
      `dependencies`.
      ```
      pip install .
      ```
      + Field `dependencies` in file `pyproject.toml` defines python libraries
        required for running the project and will first check if requirement
        already satisfied in current environment before installing the latest
        qualified version of the library.
      + Field `requires` in file `pyproject.toml` defines libraries required
        for building the project. Command `pip install` by default creates and
        uses isolated building env for building stage which completely ignores
        current user env. For example, if user already installed mpi4py==3.1.6,
        setting this field to "mpi4py>=3.1.4" will automatically install a
        mpi4py 4.0.0 in the building env and thereafter use syntax from 4.0.0
        to build PnetCDF-Python This causes version mismatch issues between
        building and running envs when numpy 2.0 and mpi4py 4.0.0 are released.
        To address this issue, use command below.
        ```
        pip install --no-build-isolation -e .
        ```

---
### User Guide

Note on configuring Read-the-Docs tool for generating PnetCDF-Python user guide.
* Read the Docs settings
  + User guide is automatically generated when new commits are pushed to the
    main branch or a new PR is created. Modify this setting of automatic action
    in the Read the Docs dashboard if needed.
  + https://app.readthedocs.org/dashboard/
  + A new repo maintainer can sign up with readthedocs using his/her github
    account
  + Adding a new repo maintainer
    * Under the project's Settings -> maintainers, a maintainer can invite
      others to become a maintainer.

* Configuration files
  + [.readthedocs.yaml](../.readthedocs.yaml) -- is a script file containing
    controls commands that run before installation of PnetCDF-Python (under
    `pre-install:`) and installation (under `python:`)
  + [docs/requirements.txt](./requirements.txt) -- is a file containing a list
    all Python package dependencies required for doc generation, including
    `sphinx`.

* Important environment variables
  + User guide generation requires environment variables set by Read the Docs
    dashboard (`Settings` -> `Environment Variables`). Delete and add a new
    variable to modify (remember to select checkbox `Public` to `Expose this
    environment variable in PR builds` if PR auto-build is enabled)
  + Current environment variables set (the only effective solution found to set
    the environment variable at installation):
     * `CC`: mpicc.mpich
     * `PNETCDF_DIR`: /home/docs/checkouts/readthedocs.org/user_builds/pnetcdf-python/checkouts/latest/_readthedocs/PnetCDF
     * `PNETCDF_VER`: 1.14.0

