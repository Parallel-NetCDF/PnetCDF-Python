## Notes for PnetCDF-python developers
---

### Note on configuring Read the Docs tool for user guide generation
 * Read the Docs settings
   * User guide is automatically generated on main branch changes and opened PR requests. Modify this in Read the Docs dashboard if needed
 * Doc files
   * `.readthedocs.yaml` -- The script that controls commands that run before installation of pnetcdf-python (under `pre-install:`) and installation (under `python:`)
   * `/docs/requirements.txt` -- Python dependencies required for doc generation, including `sphinx`
 * Important environment variables
   * User guide generation requires enviroment variables set by Read the Docs dashboard (`Admin` -> `Environment Variables`). Delete and add a new variable to modify (remember to select `Expose this environment variable in PR builds` if PR auto-build is enabled)
   * Current environment variables set (only effective solution found to set env variable at installation):
     * `CC`: mpicc.mpich
     * `PNETCDF_DIR`: /home/docs/checkouts/readthedocs.org/user_builds/pnetcdf-python/checkouts/latest/_readthedocs/PnetCDF
     * `PNETCDF_VER`: 1.12.3