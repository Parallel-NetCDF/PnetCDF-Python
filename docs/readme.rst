=============
Documentation
=============

We provide two ways to access/generate the user guide.

Generate User Guide Online
===========================

Access the user guide at https://github.com/yzanhua/pnetcdf-python

Generate User Guide in HTML
===========================

.. code-block:: bash

    # set up virtual environment
    python3 -m venv env
    source env/bin/activate
    pip install --upgrade pip
    pip install sphinx sphinx_rtd_theme

    # generate html
    cd docs
    make html

