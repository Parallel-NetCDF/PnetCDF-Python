import re
import pnetcdfpy

version_str = pnetcdfpy.__version__
pattern = r'^\d+\.\d+\.\d+$'
# Assert that the version string matches the pattern
assert re.match(pattern, version_str), f"Version string '{version_str}' does not match the expected format 'x.x.x'"
