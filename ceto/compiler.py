from .parser import parse, parse_from_cmdargs, Node, Module
from .parser import ParseException
from .semanticanalysis import semantic_analysis, macro_expansion, SemanticAnalysisError
from .codegen import codegen, CodeGenError

import os
import subprocess
import sys
import argparse
import pathlib

from time import perf_counter


cmdargs = None


def safe_unique_filename(name, extension, basepath=""):
    """
    :return:sanitized pathname with numeric suffixes added if file already exists
    """
    import glob
    name = "".join(i for i in name if i not in r'\/:*?"<>|')
    path_name = os.path.join(basepath, name)
    suffix = 1
    unique = path_name# + extension
    while glob.glob(unique + "*"):
    #while os.path.exists(unique):
        unique = path_name + "_" + str(suffix)# + extension
        suffix += 1
    return unique + extension


perf_messages = []


def compile_node(node) -> (str, Module):
    t = perf_counter()
    node = macro_expansion(node)
    perf_messages.append(f"macro time {perf_counter() - t}")
    print("after macro expand", node)
    t = perf_counter()
    node = semantic_analysis(node)
    perf_messages.append(f"semantic time {perf_counter() - t}")
    print("semantic", node)
    t = perf_counter()
    code = codegen(node)
    code = code.replace("CETO_PRIVATE_ESCAPED_UNICODE", "\\u")
    perf_messages.append(f"codegen time {perf_counter() - t}")
    print("\n".join(perf_messages))
    return code, node


def compile(cmdargs):
    t = perf_counter()
    node = parse_from_cmdargs(cmdargs)
    perf_messages.append(f"parse time {perf_counter() - t}")
    return compile_node(node)


def report_error(e):
    with open(cmdargs.filename) as f:
        source = f.read()

    if isinstance(e, ParseException):
        msg = str(e)
        msg = msg.replace("';'", "[end-of-line]")
        msg = msg[:msg.rindex("(at")]
        if hasattr(e, "_ceto_lineno"):
            line = e._ceto_lineno
        else:
            line = e.lineno
        if hasattr(e, "_ceto_col"):
            col = e._ceto_col
        else:
            col = e.col

        print("Syntax Error. Line {} Column {}:".format(line, col), file=sys.stderr)
        # print(msg, file=sys.stderr)
        # print(e.line, file=sys.stderr)
        print(source.splitlines()[line - 1], file=sys.stderr)
        print(" " * (col) + "^", file=sys.stderr)
        return
    elif isinstance(e, (SemanticAnalysisError, CodeGenError)):
        print(e.args)
        try:
            msg, node = e.args
        except ValueError:
            pass
        else:
            if isinstance(node, Node):
                loc = node.source.loc
                #source = node.source.source
                # # lineindex = source.count("\n", 0, loc)
                # beg = source.rfind("\n", loc)
                # end = source.find("\n", loc)
                # print(source[beg:end], file=sys.stderr)
                # print(" " * (beg) + "^", file=sys.stderr)
                print(e.__class__.__name__)
                print(source[loc:loc+10], file=sys.stderr)
                # print(" " * (beg) + "^", file=sys.stderr)
                print(msg, file=sys.stderr)
                return
    raise e


def main():
    ap = argparse.ArgumentParser()
    # -m / -c to mimic python
    ap.add_argument("-o", "--exename", help="Executable program name (including suffix if any)")
    ap.add_argument("-m", "--compileonly", action='store_true', help="Compile ceto code only. Do not compile C++. Do not run program.")
    ap.add_argument("--donotexecute", action='store_true', help="If compiling C++, do not attempt to run an executable")
    ap.add_argument("--_nostandardlibmacros", action='store_true', help="Do not include standard lib macros during compilation (not recommended unless compiling the standard lib macros themselves)")
    ap.add_argument("-I", "--include", type=str, nargs="*", help="Additional search directory for ceto headers (.cth files). Directory of transpiled file (first positional arg) takes priority in search.")
    ap.add_argument("filename")
    ap.add_argument("args", nargs="*")

    global cmdargs
    cmdargs = ap.parse_args()

    if not cmdargs.include:
        cmdargs.include = []

    cmdargs.filename = os.path.abspath(cmdargs.filename)
    if not os.path.isfile(cmdargs.filename):
        print("Could not find file:", cmdargs.filename, sys.stderr)
        sys.exit(-1)

    basename = str(pathlib.Path(cmdargs.filename).with_suffix(""))

    try:
        code, module = compile(cmdargs)
    except (ParseException, SemanticAnalysisError, CodeGenError) as e:
        report_error(e)
        sys.exit(-1)

    ext = ".h"
    if module.has_main_function:
        ext = ".cpp"

    if cmdargs.filename:
        if cmdargs.filename.endswith("cth"):
            ext = ".h"
            if module.has_main_function:
                print("don't put 'main' function in a header", sys.stderr)
                sys.exit(-1)
        elif cmdargs.filename.endswith("ctp"):
            ext = ".cpp"

    cmdargs.ext = ext

    cppfilename = basename + ".donotedit.autogenerated" + ext

    if ext == ".h":
        code = "#pragma once\n" + code

    with open(cppfilename, "w") as output:
        output.write(code)

    if not module.has_main_function or cmdargs.compileonly:
        sys.exit(0)

    is_msvc = sys.platform == "win32" #CXX.startswith("cl") and not CXX.startswith("clang")

    CXX = "c++"
    CXXFLAGS = f"-std=c++20 -Wall -pedantic-errors -Wconversion -Wno-parentheses -lpthread"

    if is_msvc:
        CXX = "cl.exe"

    if "CXX" in os.environ:
        CXX = os.environ["CXX"]

    if is_msvc:
        CXXFLAGS = f"/std:c++20 /Wall /permissive- /EHsc"

    if "CXXFLAGS" in os.environ:
        CXXFLAGS = os.environ["CXXFLAGS"]

    include_opts = f" -I{os.path.join(os.path.dirname(__file__))}/../include/"
    include_opts += f" -I{os.path.dirname(__file__)}"
    for inc in cmdargs.include:
        include_opts += f" -I{inc}"

    if is_msvc:
        include_opts = include_opts.replace('-I', '/I')

    CXXFLAGS += include_opts

    exename = cmdargs.exename
    if not cmdargs.exename:
        exename = basename

    if is_msvc:
        exeswitch = "/Fe" + exename
    else:
        exeswitch = "-o " + exename

    cmd = " ".join([CXX, cppfilename, exeswitch, CXXFLAGS])
    print(cmd)
    p = subprocess.Popen(cmd, shell=True)
    rc = p.wait()
    if rc != 0:
        sys.exit(rc)

    if cmdargs.donotexecute:
        return

    args = [os.path.join(".", exename)]
    if cmdargs.args:
        args += cmdargs.args

    print(" ".join(args))
    p = subprocess.Popen(args)
    rc = p.wait()
    sys.exit(rc)


if __name__ == "__main__":
    main()
