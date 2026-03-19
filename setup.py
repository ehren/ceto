# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
from setuptools.command.install import install
from glob import glob
import os
import sys
import shutil

__version__ = "0.1.2"

from setuptools import setup, find_packages
from setuptools.command.install import install


rootdir = os.path.dirname(__file__)
manifest = os.path.join(rootdir, "MANIFEST.in")

packaged_include_ceto = os.path.join(rootdir, "ceto", "ceto.h")
packaged_include_propconst = os.path.join(rootdir, "ceto", "non_null_propagate_const.h")
packaged_ast_header = os.path.join(rootdir, "ceto", "ast.cth")
packaged_utility_header = os.path.join(rootdir, "ceto", "utility.cth")
packaged_range_utility_header = os.path.join(rootdir, "ceto", "range_utility.cth")
packaged_visitor_header = os.path.join(rootdir, "ceto", "visitor.cth")

extra_packaged = [manifest, packaged_ast_header, packaged_utility_header, packaged_range_utility_header, packaged_visitor_header]

with open(manifest, "w") as f:
    f.write("""
include ceto/*.cth
include ceto/*.ctp
include ceto/*.h
include ceto/kit_local_shared_ptr/*.hpp
include ceto/kit_local_shared_ptr/detail/*.hpp
""")

for f in os.listdir(os.path.join(rootdir, "include")):
    if f.endswith(".cth"):
        if f != "python_syntax_compatibility.cth":
            dest = os.path.join(rootdir, "ceto", "ceto_private_" + f)
        else:
            dest = f
        shutil.copyfile(os.path.join(rootdir, "include", f), dest)
        extra_packaged.append(dest)

shutil.copyfile(os.path.join(rootdir, "include", "ceto.h"), packaged_include_ceto)
shutil.copyfile(os.path.join(rootdir, "include", "non_null_propagate_const.h"), packaged_include_propconst)
shutil.copyfile(os.path.join(rootdir, "selfhost", "ast.cth"), packaged_ast_header)
shutil.copyfile(os.path.join(rootdir, "selfhost", "utility.cth"), packaged_utility_header)
shutil.copyfile(os.path.join(rootdir, "selfhost", "range_utility.cth"), packaged_range_utility_header)
shutil.copyfile(os.path.join(rootdir, "selfhost", "visitor.cth"), packaged_visitor_header)

shutil.copytree(os.path.join(rootdir, "include", 'kit_local_shared_ptr'), os.path.join(rootdir, "ceto", "kit_local_shared_ptr"), dirs_exist_ok=True)

if sys.platform == "win32":
    _extra_compile_args = ["/Zc:__cplusplus", "/Wall", "/permissive-"]
    _extra_link_args = []
else:
    _extra_link_args = ["-Wl,-ldl"]
    _extra_compile_args = ["-O0", "-g3"]

ext_modules = [
    Pybind11Extension("ceto._abstractsyntaxtree",
        ["selfhost/ast.donotedit.cpp"],
        define_macros = [('CETO_UNSAFE_ALLOW_NON_NULL_PTR_DEFAULT_CONSTRUCTION', '1')],  # pybind11 holder type needs to be default constructible
        cxx_std=20,
        include_dirs=["include", "selfhost/thirdparty", "include/kit_local_shared_ptr"],
        extra_compile_args=_extra_compile_args,
        extra_link_args=_extra_link_args
    ),
]

setup(
    name="ceto",
    packages = ["ceto"],
    entry_points = {
        'console_scripts': ['ceto=ceto.compiler:main'],
    },
    cmdclass={
        'build_ext': build_ext,
        'install': install,
    },
    version=__version__,
    author="Ehren Metcalfe",
    author_email="ehren.m@gmail.com",
    url="https://github.com/ehren/ceto",
    description="General purpose programming language transpiled to C++",
    long_description="Parens/call expression language transpiled to c++20. \"Python\" with 2 parentheses moved or inserted (with extra C++ syntax). Codegen based on https://github.com/lukasmartinelli/py14 with additions e.g. implicit make_shared/unique, checked autoderef via '.', swiftish lambda capture, implicit move from last use of unique, const by default, extra CTAD!",
    ext_modules=ext_modules,
    include_package_data=True,
    extras_require={"test": "pytest"},
    install_requires=[
        'cpyparsing',  # pyparsing also supported
        'colorama',
    ],
    zip_safe=False,
    python_requires=">=3.9",
)
