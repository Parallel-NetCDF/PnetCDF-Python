=============
Documentation
=============

We provide two ways to access/generate the user guide.

Generate User Guide Online
===========================

Access the user guide at https://yzanhua.github.io/pncpy-doc/index.html

Generate User Guide in HTML
===========================

.. code-block:: bash

    # set up virtual environment
    python3 -m venv env
    source env/bin/activate
    pip install --upgrade pip
    pip install sphinx sphinx_rtd_theme sphinx-autodoc-typehints
    ## install PnetCDF Python

    # generate html
    cd docs
    make html

Note that every time you make changes to the source code's doc string, you need to
reinstall the library and then ``make html`` again to update the user guide.

