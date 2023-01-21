from parser import parse
from semanticanalysis import semantic_analysis
from codegen import codegen
from preprocessor import preprocess

import os
import subprocess
import io

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


def compile(s, compile_cpp=True):
    perf_messages = []
    t = perf_counter()
    expr = parse(s)
    perf_messages.append(f"parse time {perf_counter() - t}")
    t = perf_counter()
    expr = semantic_analysis(expr)
    perf_messages.append(f"semantic time {perf_counter() - t}")
    print("semantic", expr)
    t = perf_counter()
    code = codegen(expr)
    perf_messages.append(f"codegen time {perf_counter() - t}")

    # print("code:\n", code)
    output = None

    if compile_cpp:
        build_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "build")
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        filename = safe_unique_filename("generatedcode", ".cpp", basepath=build_dir)

        with open(filename, "w") as file:
            file.write(code)
        import platform
        if "Darwin" in platform.system():
            # need to upgrade
            command = "clang++ " + filename + " -std=c++2a -Wall -Wno-parentheses && echo 'done compile'"
            # command = "clang++ " + filename + " -std=c++17 -Wall -Wno-parentheses && echo 'done compile'"
        else:
            # command = "clang++ " + filename + " -std=c++20 -Wall -Wno-parentheses && echo 'done compile'"
            command = "g++ " + filename + " -std=c++20 -Wall -pedantic-errors -Wno-parentheses && echo 'done compile'"

        print("\n".join(perf_messages))

        t1 = perf_counter()
        p = subprocess.Popen(command, shell=True)

        # sio = io.StringIO(s)
        # t = perf_counter()
        # preprocess(sio).getvalue()  # still have to run the 'pre'processor due to insufficient indent checking in current grammar
        # print("indent checking time", perf_counter() - t)

        output, error = p.communicate()
        print("c++ compiling time", perf_counter() - t1)

        output = subprocess.check_output('./a.out').decode("utf-8")#, shell=True)
        print(output)

        os.remove(filename)
        os.remove('./a.out')

    return output


if __name__ == "__main__":

    # x + y = x.add(y)? or rather x.oper=(y)


    0 and compile("""
# def (default_args, x=[1], y=2, z = lambda (zz, return 1):
def (default_args, x=[1], y=2: #, z = lambda (1):
    x.append(2)
    # x.push_back(2)
    printf("%d\n", z(y))
    return x
)

def (main:
    default_args()
)
    """)


    0 and compile("""
    
def (map, foo, x:
    return: foo(x:int):int  # these types do nothing right now
)
    
# def (fibonacci, n:
#     if (n == 0:
#         return: 0
#     elif: n == 1:
#         return: 1
#     else:
#         return: fibonacci(n - 1) + fibonacci(n - 2)
#     )
# )

def (blah, x:int :
    printf("blah %d", x)
    return: x
)

def (main:
    # printf("%d", fibonacci(10))
    # ()
    # (1,2)
    # (1)
    x = []
    x.append(5)
    map(blah, 15)
    
    y = []
    z = 5
    q = z
    y.append(q)
    
    return: 0
)
    """)


    0 and compile("""
def (foo, x, bar:
    # printf("%d uh oh", w)
    if (x:
        y = 1
        if (y:
            z = 1
            if (z:
                w = 5
            else:
                z = 2
            )
        )
    else:
        y = 2
    )
    
    printf("here's some more output %d", w)
    if (x:
        # bar(x-1, nullptr)
        foo(x, nullptr)
    )
)

def (main:
    printf("hello world! %d", 2)
    foo(5, nullptr)
    return: 0
)
    """)

    0 and compile("""
    
def (map, values:[int]:positional_only, fun:
    # results = [1]
    results = []
    # results = 1
    print(results)
    results.append(fun())
    results[0]
   # for v in values:
   #     results.append(fun(v))
   # return results
   #  i = 0
   #  x = i
   #  i = x
   #  (z = i+1)
   #  (x+5)
   #  (,)
   #  (1,2)
   #  (1,)
   #  (1)
    
    if (i + 5:
        results.append(fun(v))
        results.pop()
        pass
    )
    return results
)
    
    """)



    0 and compile("""
def (foo, c:
    y
    c
    x
    z
    blah(z)
    return blah(x)
    return: blah(x)
)
    
def (main:
    w = w
    y = x
    y
    # x = y
    a + (z = y)
    
    def (blah, c:
        y
        c
        x
        z
        blah(z)
        return blah(x)
        return: blah(x)
    )
    
    blah(z)
)
    """)

    0 and compile("""
             
def (main:
    # if ((x:int): y=0:int elif (x:int): 5:int else x=2:int) # correct
    # if ((x:int): y=0:int, elif: (x:int): 5:int, else: x=2:int) # correct
    # 
    if (x=5:
        6
    elif x = 5:
        6
        6
        return
    else:
        a[10]
        10[a]()
        10
        return: 15:int
    )
    
    try (:
        1
    # except ((DarnError as d): Exception):
    except DarnError as d: Exception:
        2
    except DarnError as d:
        2
        2
    except e: DarnError:
        p
    except e:
        0
        0
    except:
        0
        0
    )
    
    if ((x=10): 2 elif: (x=2): return 5:int else: return)
    # x as + 5
    
    
    bar (x=10:foo, (x=10):foo, (x=10:foo))
    
    
    # try(e: 1 except: DarnError: d: 2:int except: 0)
)
    """)


    0 and compile("""
# (1+2)(:
#     ")hi"
    
# )
def(y:
    foo(:
        1 :(
              type)
    a:int:
        x : cpp: ptr:[int]
    )
)
    """)

    0 and compile("""
def (main:
    if (x:
        dostuff()
    elif y + 2:
        otherstuff()
        1 + 5 : (
int)
    else:
        darn()
    )
    if ((x:int):y=0:int elif (x:int): 5:int else x=2:int) # correct
    
    # if ((x:int):y=0:int,elif:(x:int):5:int, else:x=2:int) # correct
    
    (foo()+1)(1)
    ((1+redundant))(1)
    (1+2)(1)
    2(1)
    (1+2)*3("blah", x=y)
    ((1+2)*3)("blah", (x=y))
    
    (1+2)(:
        blah
    )
    
    
)
    """)

    # test named parameters....
    # test named parameters....
    0 and compile("""
def (main:
    foo((x=y:int:strong), x=y:int:weak)
    foo(x=y:int, (z=y:int))
    (1+1)
)
    """)

    0 and compile("""
def (main:
    # if (1:1)
    if (if(1:1):1)
    # def (x,1)
    # if (1: 1, elif: x: 2, else: 0)
    # if (elif:x:int:5:int) # should result in "unknown identifier 'elif'"
    if ((x:int):0:int, elif:(x:int):5:int)  # works
    # if (x:int:y=0:int,elif:x:int:5:int, else:x=2:int) # nonsense but lowered correctly
    # if ((x:int):y=0:int,elif:(x:int):5:int, else:x=2:int) # correct
    # y=((x=123456789))
)""")

    0 and compile("""
def (bar, x, y, 0)
def (foo, x, y:
    # parser: [Module([def(['bar', 'x', 'y', 0]), def(['foo', 'x', 'y', Block([[if([:(x,int), :(1,int), :(elif,:(-(x,1),int)), :(5,int), :(else,:(0,int))])], 
    #[if([:(1,1), 
    # :(elif,:(:(x,int),:(5,int))), 
    # :(else,:(0,int))])]])])])]

    #if (x:int, 1:int, elif:x-1:int, 5:int, else: 0:int)
    #[if([:(1,1), 
    # :(elif, :(x,:(int,:(5,int)))), 
    # :(else,0)])]
    #if (1:1, elif:x:int:5:int, else: 0:int)
    if (1:1)
    if (elif:x:int:5:int) # should result in "unknown identifier 'int'"
    if (elif:(x:int):5:int)
    #if (1:1, elif:(x:int):5:int, else: 0:int)
    #if (1:1, elif:x:5, else: 0)
)""")

    0 and compile("""
def (bar, x, y, 0)
def (foo, x, y:
    if (1:
        print("1")
        2
    )

    if (2:
        5
    elif: y: 2, else: 0)

    if (x:int, 5:int, elif: x = y : int, 0, else: 0)
    if (x:int, 1, elif:x-1:int, 5, else: 0)
    if (x:int, 1:int, elif:x-1:int, 5:int, else: 0:int)
    #if (x:int, 1, elif:x+1: 0:int)  # invalid if semantics
    if (x:int, 1, elif:x+1, 0:int, else: 5)
    if (x, 1, elif: y, 2)
    x=if (x, 1)
    lambda (x, y, z:int, 0)
    lambda (x:int, y:int, z:int:
        0
    )
    lambda(1)
    lambda(:
        1
    )
    lambda(x:int:
        1
    )
    lambda(x:int, 1)
)

    """)


    0 and compile("""
if (x: 
    y
    x+1
    3
    z = 5+4
)
foo(x,y)
foo(x,y)""")
