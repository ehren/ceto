from .parser import parse, Module
from .semanticanalysis import semantic_analysis
from .codegen import codegen

import os
import subprocess
import sys
import argparse
import pathlib

from time import perf_counter


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


def compile(s) -> (str, Module):
    perf_messages = []
    t = perf_counter()
    node = parse(s)
    perf_messages.append(f"parse time {perf_counter() - t}")
    t = perf_counter()
    node = semantic_analysis(node)
    perf_messages.append(f"semantic time {perf_counter() - t}")
    print("semantic", node)
    t = perf_counter()
    code = codegen(node)
    perf_messages.append(f"codegen time {perf_counter() - t}")
    print("\n".join(perf_messages))
    return code, node


def runtest(s, compile_cpp=True):
    code, _ = compile(s)

    output = None

    if compile_cpp:
        build_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "build")
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        filename = os.path.join(build_dir, "testsuitegenerated.cpp")

        with open(filename, "w") as f:
            f.write(code)

        if "CXX" in os.environ:
            CXX = os.environ["CXX"]
        else:
            CXX = "c++"

        if CXX == "cl":
            CXXFLAGS = f"/std:c++20 /Wall /permissive- /EHsc /I{os.path.join(os.path.dirname(__file__))}/../include/"
            exe_name = "testsuitegenerated.exe"
        else:
            CXXFLAGS = f"-std=c++20 -Wall -pedantic-errors -Wconversion -Wno-parentheses -lpthread -I{os.path.join(os.path.dirname(__file__))}/../include/"
            exe_name = "./a.out"

        command = f"{CXX} {filename} {CXXFLAGS}"

        print(command)

        t1 = perf_counter()
        p = subprocess.Popen(command, shell=True)

        output, error = p.communicate()
        print("c++ compiling time", perf_counter() - t1)

        output = subprocess.check_output(exe_name).decode("utf-8")#, shell=True)
        print(output)

        os.remove(os.path.join(".", filename))
        os.remove(exe_name)

        if CXX == "cl":
            output = output.replace("\r\n", "\n")

    return output


from pyparsing import ParseException


def report_error(e : ParseException, source : str):
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


def main():
    ap = argparse.ArgumentParser()
    # -m / -c to mimic python
    ap.add_argument("-m", "--compileonly", action='store_true', help="Compile ceto code only. Do not compile C++. Do not run program.")
    ap.add_argument("-c", "--runstring", help="Compile and run string", action="store_true")
    ap.add_argument("-i", "--implementation", help="Create an implementation (.cpp) file even if filename does not end in .ctp", action="store_true")
    ap.add_argument("--no-pragma-once", help="Do not automatically add a '#pragma once' include guard to a header", action="store_true")
    ap.add_argument("filename")
    ap.add_argument("args", nargs="*")
    cmdargs = ap.parse_args()

    if cmdargs.runstring:
        source = cmdargs.filename
        basename = safe_unique_filename("cetodashccode", extension="")

    else:
        with open(cmdargs.filename) as f:
            source = f.read()
        basename = str(pathlib.Path(cmdargs.filename).with_suffix(""))

    try:
        code, module = compile(source)
    except ParseException as e:
        report_error(e, source)
        sys.exit(-1)

    ext = ".h"
    if module.has_main_function or cmdargs.implementation:
        ext = ".cpp"

    if cmdargs.filename:
        if cmdargs.filename.endswith("cth"):
            ext = ".h"
            if module.has_main_function:
                print("don't put 'main' function in a header", sys.stderr)
                sys.exit(-1)
            if cmdargs.implementation:
                print("-i/--implementation incompatible with .cth (header) extension", sys.stderr)
                sys.exit(-1)
        elif cmdargs.filename.endswith("ctp"):
            ext = ".cpp"

    cppfilename = basename + ext

    if ext == ".h" and not cmdargs.no_pragma_once:
        code = "#pragma once\n" + code + "\n#end\n"

    with open(cppfilename, "w") as output:
        output.write(code)

    if not module.has_main_function or cmdargs.compileonly:
        sys.exit(0)

    CXX = "c++"
    CXXFLAGS = f"-std=c++20 -Wall -pedantic-errors -Wconversion -Wno-parentheses -lpthread -I{os.path.join(os.path.dirname(__file__))}/../include/"
    if "CXX" in os.environ:
        CXX = os.environ["CXX"]
    if "CXXFLAGS" in os.environ:
        CXXFLAGS = os.environ["CXXFLAGS"]

    exename = basename

    cmd = " ".join([CXX, cppfilename, "-o " + exename, CXXFLAGS])
    print(cmd)
    p = subprocess.Popen(cmd, shell=True)
    rc = p.wait()
    if rc != 0:
        sys.exit(rc)

    args = [os.path.join(".", exename)]
    if cmdargs.args:
        args += cmdargs.args

    print(" ".join(args))
    subprocess.Popen(args)


if __name__ == "__main__":
    main()
