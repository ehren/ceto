# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
import os

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)


if 'CPPFLAGS' in os.environ:
    os.environ['CPPFLAGS'] += "-I./include"
else:
    os.environ['CPPFLAGS'] = "-I./include"

ext_modules = [
    Pybind11Extension("abstractsyntaxtree",
        ["selfhost/ast.cpp"],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
		cxx_std=20
        ),
]

setup(
    name="ceto",
    version=__version__,
    author="Ehren Metcalfe",
    author_email="ehren.m@gmail.com",
    url="https://github.com/ehren/ceto",
    description="A test project using pybind11",
    long_description="",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
