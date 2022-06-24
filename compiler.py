from parser import parse
from semanticanalysis import semantic_analysis
from codegen import codegen




def compile(s):
    expr = parse(s)
    expr = semantic_analysis(expr)
    print("semantic", expr)
    code = codegen(expr)
    print("code:\n", code)


if __name__ == "__main__":
    compile("""
    
def (map, values, fun:
    results = []
   # for v in values:
   #     results.append(fun(v))
   # return results
    i = 0
    while (i + 5:
        # results.append(fun(v))
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
