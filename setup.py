# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
from glob import glob
import os

__version__ = "0.1.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)


#if 'CPPFLAGS' in os.environ:
#    os.environ['CPPFLAGS'] += "-I./include"
#else:
#    os.environ['CPPFLAGS'] = "-I./include"

ext_modules = [
    Pybind11Extension("ceto._abstractsyntaxtree",
        ["selfhost/ast.cpp"],
        #define_macros = [('VERSION_INFO', __version__)],
        cxx_std=20,
        include_dirs=["include"]
    ),
]

setup(
    name="ceto",
    packages = ["ceto"],
    entry_points = {
        'console_scripts': ['ceto=ceto.compiler:main'],
    },
    version=__version__,
    author="Ehren Metcalfe",
    author_email="ehren.m@gmail.com",
    url="https://github.com/ehren/ceto",
    description="General purpose programming language transpiled to C++",
    long_description="Parens/call expression language transpiled to c++20. \"Python\" with 2 parentheses moved or inserted (with extra C++ syntax). Codegen based on https://github.com/lukasmartinelli/py14 with additions e.g. implicit make_shared/unique, checked autoderef via '.', swiftish lambda capture, implicit move from last use of unique, const by default, extra CTAD!",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    install_requires=[
        'pyparsing',
    ],
    #cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
