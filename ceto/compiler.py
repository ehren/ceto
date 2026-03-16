from .parser import parse, parse_from_cmdargs, Node, Module
from .parser import ParseException
from .semanticanalysis import semantic_analysis, macro_expansion, SemanticAnalysisError
from .codegen import codegen, CodeGenError

import os
import subprocess
import sys
import argparse
import pathlib
import colorama

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

    colorama.init(autoreset=True) 

    # inital setup of slm
    package_dir = pathlib.Path(__file__).parent
    install_success_path = package_dir / "install_was_successful.py"
    with open(install_success_path, "r+") as f:
        install_success = f.read().strip()
        if install_success != "True" and not (len(sys.argv) > 1 and sys.argv[1] == '--_firsttimecompile'):
            print(colorama.Fore.RED + "COMPILING STANDARD LIBRARY MACROS FOR FIRST TIME (THIS WILL TAKE A WHILE)\n\n\n")
            compile_slm = subprocess.run(["ceto", "--_firsttimecompile", package_dir / "install_standard_library_macros.ctp"])
            if compile_slm.returncode != 0:
                print("COMPILING STANDARD LIBRARY MACROS FAILED (SOMETHING IS BROKEN)")
                print("NOTE: It's possible you forgot to run 'ceto' after installation (no arguments required) with the required permissions to write to your python package dir (same permissions as when running pip install). This is likely not the issue if you're using a virtualenv.")
                sys.exit(-1)
            f.seek(0)
            f.write("True")
            f.truncate()
            print(colorama.Fore.GREEN + "STANDARD LIBRARY MACROS (THE SLM) COMPILED SUCCESSFULLY - subsequent ceto invocations will be much faster")
            if len(sys.argv) == 1:
                sys.exit(0)

    ap = argparse.ArgumentParser()
    # -m / -c to mimic python
    ap.add_argument("-o", "--exename", help="Executable program name (including suffix if any)")
    ap.add_argument("-m", "--compileonly", action='store_true', help="Compile ceto code only. Do not compile C++. Do not run program.")
    ap.add_argument("--donotexecute", action='store_true', help="If compiling C++, do not attempt to run an executable")
    ap.add_argument("--_noslm", action='store_true', help="Do not include standard lib macros during compilation (not recommended unless compiling the standard lib macros themselves)")
    ap.add_argument("--_norefs", action='store_true', help="Enable experimental mode to ban unsafe use of C++ references (without unsafe annotation). Currently implemented: ban all C++ references from subexpressions: An expression returning a reference must either be discarded or must be on the lhs of an Assignment (requiring a 'ref' type annotion if the reference is to be preserved instead of a copy). TODO: additional unsafe annotation for const:ref / mut:ref locals/members and mut:ref params")
    ap.add_argument("--_firsttimecompile", action='store_true', help="Ignore this: Internal option to compile standard library macros before the first program runs")
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
        if isinstance(e, CodeGenError) and ("Unknown scope resolution" in str(e) or "call to unknown function" in str(e)):
            # horrible hack - interaction between name lookup and macro expansion causes spurious name lookup errors with function calls that originate from a macro expansion
            # only occurs on the first run when the macro is first compiled (could be a subtle difference in code paths of macro expansion in first time vs cached case)
            # (python side scope handling is also brittle). TODO find the real issue but let's just bypass it for now by trying again:
            try:
                code, module = compile(cmdargs)
                e = None
            except (ParseException, SemanticAnalysisError, CodeGenError) as e2:
                e = e2
        if e:
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

    cppfilename = basename + ".donotedit" + ext

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
    include_opts = f" -I{os.path.join(os.path.dirname(__file__))}/../include/kit_local_shared_ptr"
    include_opts += f" -I{os.path.dirname(__file__)}"
    include_opts += f" -I{os.path.dirname(__file__)}/kit_local_shared_ptr"
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
