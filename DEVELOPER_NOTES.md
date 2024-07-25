## Notes for PnetCDF-python developers
---

### Note on configuring Read the Docs tool for user guide generation
 * Doc files
   * `.readthedocs.yaml` -- The script that controls commands that run before installation of pnetcdf-python (under `pre-install:`) and installation (under `python:`)
   * `/docs/requirements.txt` -- Python dependencies required for doc generation, including `sphinx`
 * Important environment variables
   * User guide generation requires enviroment variables set by Read the Docs dashboard (`Admin` -> `Environment Variables`). Delete and add a new variable to modify
   * Current environment variables set:
     * `CC`: mpicc.mpich
     * `PNETCDF_DIR`: /home/docs/checkouts/readthedocs.org/user_builds/pnetcdf-python/checkouts/latest/_readthedocs/PnetCDF
     * `PNETCDF_VER`: 1.12.3