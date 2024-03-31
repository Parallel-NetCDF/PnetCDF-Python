# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PnetCDF Python'
copyright = '2023, CUCIS'
author = 'CUCIS'
release = '0.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx_autodoc_typehints',
    'autoapi.extension'
]
autoapi_dirs = ['../../src']
templates_path = ['_templates']
exclude_patterns = []

autodoc_typehints = 'signature'



# autodoc_mock_imports = ["mpich", "libmpich-dev", "libhdf5-mpich-dev", "numpy", "cython", "cftime" , "pytest", "twine", "wheel", "check-manifest", "mpi4py"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    "body_max_width": "none",
}
html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": "NU-CUCIS", # Username
    "github_repo": "pnetcdf-python", # Repo name
    "github_version": "main", # Version
    "conf_py_path": "/docs/source/installation", # Path in the checkout to the docs root
}
autodoc_default_options = {
    'members': True,
    'no-undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
}

def autodoc_skip_member(app, what, name, obj, skip, options):
    # Ref: https://stackoverflow.com/a/21449475/
    exclusions = ('name', 'datatype', 'size', 'shape', 'dimensions')
    exclude = name in exclusions
    # return True if (skip or exclude) else None  # Can interfere with subsequent skip functions.
    return True if exclude else None
 
def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)