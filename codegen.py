import typing
from typing import Union, Any

from semanticanalysis import Node, Module, Call, Block, UnOp, BinOp, \
    ColonBinOp, Assign, NamedParameter, Identifier, IntegerLiteral, IfNode, \
    SemanticAnalysisError, SyntaxColonBinOp, find_def, find_use, find_uses, \
    find_all, find_defs, is_return, is_void_return, RebuiltCall, RebuiltIdentifer, build_parents, find_def_starting_from
from parser import ListLiteral, TupleLiteral, ArrayAccess, StringLiteral, AttributeAccess, RebuiltStringLiteral, CStringLiteral


import io
from collections import defaultdict


class CodeGenError(Exception):
    pass

# A : :T.func()
# A of type :T.func()
# (A::T).func() # (A of Type :T).func()
# (A::T).(func:int)()
# namespace(A, T).template_instantiate(int, func())

unused_cpp = """
// https://stackoverflow.com/questions/14466620/c-template-specialization-calling-methods-on-types-that-could-be-pointers-or/14466705#14466705
/*
template<typename T>
T* get_ptr(T & obj) { return &obj; } // turn reference into pointer!

template<typename T>
std::shared_ptr<T> get_ptr(std::shared_ptr<T> obj) { return obj; } // obj is already pointer, return it!

*/

//template<typename T>
//T* get_ptr(T* obj) { return obj; } // obj is already pointer, return it!


template <typename Fun>
struct is_fun_ptr
    : std::integral_constant<bool, std::is_pointer<Fun>::value
                            && std::is_function<
                                   typename std::remove_pointer<Fun>::type
                               >::value>
{
};

// https://stackoverflow.com/questions/18666218/stdenable-if-is-function-pointer-how
// https://stackoverflow.com/questions/41853159/how-to-detect-if-a-type-is-shared-ptr-at-compile-time
// https://stackoverflow.com/questions/20709896/how-do-i-use-stdenable-if-with-a-self-deducing-return-type
enum class enabler_t {};

template<typename T>
using EnableIf = typename std::enable_if<T::value, enabler_t>::type;



template<class T>
struct is_shared_ptr : std::false_type {};

template<class T>
struct is_shared_ptr<std::shared_ptr<T>> : std::true_type {};


/*
//template <class Fun&, typename = typename std::enable_if<!is_fun_ptr<std::remove_reference<Fun>>::value && !is_shared_ptr<std::remove_reference<Fun>>::value, void>::type>
template <class Fun, typename = typename std::enable_if<!is_fun_ptr<Fun>::value && !is_shared_ptr<Fun>::value, void>::type>
//typename std::enable_if<!is_fun_ptr<Fun>::value && !is_shared_ptr<Fun>::value>::type
auto get_ptr(Fun& f, typename std::enable_if<!is_fun_ptr<Fun>::value && !is_shared_ptr<Fun>::value, void>::type * dummy = nullptr) {
//Fun* get_ptr(Fun f) {
    return &f;
}

template <class Fun, typename = typename std::enable_if<is_fun_ptr<Fun>::value, void>::type>
auto get_ptr(Fun f, typename std::enable_if<is_fun_ptr<Fun>::value, void>::type * dummy = nullptr) {
    return f;
}

template <class Fun, typename = typename std::enable_if<is_shared_ptr<Fun>::value, void>::type>
auto get_ptr(Fun f, typename std::enable_if<is_shared_ptr<Fun>::value, void>::type * dummy = nullptr) {
    return f;
}*/

/*
template<typename Obj>
Obj* get_ptr(Obj& o)
{
    if constexpr (is_fun_ptr<std::remove_reference<Obj>>::value) {
        return o;
    } else {
        return &o;
    }

    if constexpr (std::is_function_v<std::remove_pointer_t<Obj>>)
    #     o();
    # else
    #     o.print();
}
*/
/*
template <class Fun, typename = typename std::enable_if<is_fun_ptr<Fun>::value, void>::type>
auto get_ptr(Fun f) -> Fun {
//Fun* get_ptr(Fun f) {
    return f;
}

template <class Fun, typename = typename std::enable_if<is_shared_ptr<Fun>::value, void>::type>
auto get_ptr(Fun f) -> Fun{
//Fun* get_ptr(Fun f) {
    return f;
}*/

/*
template <typename Fun>
typename std::enable_if<is_fun_ptr<Fun>::value>::type
//auto get_ptr(Fun f)  -> Fun {
Fun get_ptr(Fun f) {
    return f;
}

 template <typename Fun>
 typename std::enable_if<is_shared_ptr<Fun>::value>::type
//auto get_ptr(Fun f) -> Fun {
Fun get_ptr(Fun f) {
     return f;
}
*/

/*
struct object : std::enable_shared_from_this<object> {
    virtual std::shared_ptr<object> foo() {
        return shared_from_this();
    }
    virtual ~object() {
    };
};*/

/*
// https://stackoverflow.com/questions/657155/how-to-enable-shared-from-this-of-both-parent-and-derived/32172486#32172486
template <class Base>
class enable_shared_from_base
  : public std::enable_shared_from_this<Base>
{
protected:
    template <class Derived>
    std::shared_ptr<Derived> shared_from_base()
    {
        return std::static_pointer_cast<Derived>(shared_from_this());
    }
};

struct object : public enable_shared_from_base<object> {
    virtual ~object() {
    };
};
*/





/*
template <typename T, typename Y>
auto add(std::shared_ptr<T> t, std::shared_ptr<Y> y)
{
    if constexpr (std::is_base_of_v<object, T>) {
        return  (*t) + y;
    } else {
        return t + y;
    }
}
*/



template<typename T, typename ...TAIL>
void print(const T &t, TAIL... tail) {
    std::cout << t << ' ';
    print(tail...);
}




class Integer : public object {
private:
    long long integer;
public:
    Integer() : integer(0) {}
    
    Integer(long long i) : integer(i) {}
    
    std::shared_ptr<Integer> operator+(const Integer & other) const {
        return std::make_shared<Integer>(this->integer + other.integer);
    }    

};


/*
//template<typename T>
template<typename T, typename Y>
//std::shared_ptr<T> add(std::shared_ptr<T> a, std::shared_ptr<T> b) {
//auto add(std::shared_ptr<T> a, std::shared_ptr<T> b) {
auto add(std::shared_ptr<T> a, Y b) {
//std::shared_ptr<object> add(std::shared_ptr<object> a, std::shared_ptr<object> b) {
    //return *a + *b;  // works with traditional c++ double dispatch implementation (other arg taken by const reference)
    
    // but if we allow java style implementation in our language:
    // oh also see changes to second arg above
    return *a + b;
    
    
    
    // just no:
    // return std::static_pointer_cast<*a + *b;
    //return (*a).T::operator+(*b);
}*/

/*
template<typename T>
std::enable_if_t<!std::is_base_of_v<object, T>, std::shared_ptr<T>>
T add(T a, T b) {
    return a + b;
}*/


template<typename T> struct is_shared_ptr : std::false_type {};
template<typename T> struct is_shared_ptr<std::shared_ptr<T>> : std::true_type {};

/*
template <class T> 
typename std::enable_if<is_shared_ptr<decltype(std::declval<T>().value)>::value, void>::type
func( T t )
{
    std::cout << "shared ptr" << std::endl;
}

template <class T> 
typename std::enable_if<!is_shared_ptr<decltype(std::declval<T>().value)>::value, void>::type
func( T t )
{
    std::cout << "non shared" << std::endl;
}
*/

/*
template<typename T>
std::enable_if<!is_shared_ptr<decltype(std::declval<T>().value)>::value, T>::type
add(T a, T b) {
    return a + b;
}


template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>>
get_ptr(std::shared_ptr<T> obj) { return obj; }


template<typename T, typename Y>
auto add(std::shared_ptr<T> a, Y b) {
    return *a + b;
}*/

// kinda works (but no return type deduction):
/*
template<typename T, typename Y>
std::enable_if_t<std::is_base_of_v<object, T> && !std::is_base_of_v<object, Y>, std::shared_ptr<object>>
add(std::shared_ptr<T> a, Y b) {
    return *a + b;
}*/

/*
template<class T, typename = typename std::enable_if<std::is_base_of_v<object, T>, void>::type>, class Y, typename = typename std::enable_if<!std::is_base_of_v<object, Y>, void>::type>
auto add(T t, typename std::enable_if<std::is_base_of_v<object, T>::value, void>::type* dummy1 = nullptr, Y y, typename std::enable_if<!std::is_base_of_v<object, Y>::value, void>::type* dummy2 = nullptr) {
    return *t + y;
}*/


/*
template<class T, typename = typename std::enable_if<std::is_integral<T>::value, void>::type>
auto function(T t, typename std::enable_if<std::is_integral<T>::value, void>::type* dummy = nullptr) {
    std::cout << "integral" << std::endl;
    return 0;
}*/



/*template<typename T>
auto add(T a, T b) {
    static_assert
    return a + b;
}*/



/*template<typename T  >
auto add(T a, T b) {
    static_assert
    return a + b;
}*/

/*
template<typename T>
std::shared_ptr<T> get_ptr(std::shared_ptr<T> obj) { return obj; }
*/

"""


cpp_preamble = """
#include <memory>
#include <vector>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <type_traits>
#include <utility>
#include <compare> // for <=>


struct object {
};

struct shared_object : public std::enable_shared_from_this<shared_object>, object {
    virtual ~shared_object() {
    };
    
    template <typename Derived>
    std::shared_ptr<Derived> shared_from_base() {
        return std::static_pointer_cast<Derived>(shared_from_this());
    }
    
    /*
    virtual std::shared_ptr<object> operator+(const object& other) const {
        printf("not implemented\\n");
        return {};
    }*/    
    
    ___PLACE_TO_PUT_JUNK
};

// dunno about this one, needed for calling methods on string temporaries...
template<typename T>
T* get_ptr(T && obj) { return &obj; }

template<typename T>
T* get_ptr(T & obj) { return &obj; }

template<typename T>
T* get_ptr(T* obj) { return obj; } // obj is already pointer, return it!

template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::shared_ptr<T>>
get_ptr(std::shared_ptr<T> obj) { return obj; }

template<typename T>
std::enable_if_t<std::is_base_of_v<object, T>, std::unique_ptr<T>&>
get_ptr(std::unique_ptr<T>& obj) { return obj; }

/*
template <typename T, typename Y>
auto add(std::shared_ptr<T> t, Y y)
{
    if constexpr (std::is_base_of_v<object, T>) {
        return  *t + y;
    } else {
        return t + y;
    }
}

template <typename Y, typename T>
auto add(Y y, std::shared_ptr<T> t)
{
    if constexpr (std::is_base_of_v<object, T>) {
        return y + *t;
    } else {
        return y + t;
    }
}

template <typename T>
auto add(std::shared_ptr<T> t, std::shared_ptr<T> y)
{
    if constexpr (std::is_base_of_v<object, T>) {
        return *t + y;
    } else {
        return t + y;
    }
}

template <typename T>
std::enable_if_t<!std::is_convertible_v<T, std::shared_ptr<object>>, T>
add(T a, T b)
{
    return a + b;
}*/





"""


# Uses code and ideas from https://github.com/lukasmartinelli/py14

# https://brevzin.github.io/c++/2019/12/02/named-arguments/



class Context:

    def __init__(self):
        self.interfaces = defaultdict(list)
        self._indent = 0
        self.parent = None

    def indent_str(self):
        return "    " * self._indent

    def new_scope_context(self):
        c = Context()
        c.interfaces = self.interfaces  # shallow copy
        c.parent = self
        c._indent += 1
        return c


# method_declarations = []
cstdlib_functions = ["printf", "fprintf", "fopen", "fclose"]


def codegen_if(ifcall : Call, cx):
    assert isinstance(ifcall, Call)
    assert ifcall.func.name == "if"

    ifnode = IfNode(ifcall.func, ifcall.args)

    indt = cx.indent_str()

    scopes = [ifnode.cond, ifnode.thenblock, ifnode.elseblock]
    for elifcond, elifblock in ifnode.eliftuples:
        scopes.append(elifcond)
        scopes.append(elifblock)

    assigns = []

    def stop(n):
        return isinstance(n, Block) and n.parent.func.name not in ["if", "while"]

    for scope in scopes:
        # assigns.extend(find_all(scope, test=lambda n: (isinstance(n, Assign) and not (isinstance(n.parent, Call) and n.parent.func.name == 'if')), stop=stop))
        assigns.extend(find_all(scope, test=lambda n: isinstance(n, Assign), stop=stop))

    print("all if assigns", list(assigns))

    declarations = {}

    for assign in assigns:
        if hasattr(assign, "already_declared"):
            continue
        # if not isinstance(assign.parent, Block):
            # don't do any funky auto auto declarations for non-block scoped assigns
            # uh or not
        #     continue
        if isinstance(assign.lhs, Identifier) and not find_def(assign.lhs):
            assign.already_declared = True
            if assign.lhs.name in declarations:
                continue
            declarations[str(assign.lhs)] = codegen_node(assign.rhs, cx)

    cpp = ""
    for lhs in declarations:
        cpp += f"decltype({declarations[lhs]}) {lhs};\n" + indt

    cpp += "if (" + codegen_node(ifnode.cond, cx) + ") {\n"
    cpp += codegen_block(ifnode.thenblock, cx.new_scope_context())

    for elifcond, elifblock in ifnode.eliftuples:
        cpp += indt + "} else if (" + codegen_node(elifcond, cx.new_scope_context()) + ") {\n"
        cpp += codegen_block(elifblock, cx.new_scope_context())

    if ifnode.elseblock:
        cpp += indt + "} else {\n"
        cpp += codegen_block(ifnode.elseblock, cx.new_scope_context())

    cpp += indt + "}"

    return cpp


def codegen_for(node, cx):
    assert isinstance(node, Call)
    assert len(node.args) == 2
    instmt = node.args[0]
    block = node.args[1]
    if not isinstance(block, Block):
        raise CodeGenError("expected block as last arg of if", node)
    if not isinstance(instmt, BinOp) and instmt.func == "in": # fix non node args
        raise CodeGenError("unexpected 1st argument to for", node)
    var = instmt.lhs
    iterable = instmt.rhs
    indt = cx.indent_str()
    # forstr = indt + 'for(const auto& {} : {}) {{\n'.format(codegen_node(var), codegen_node(iterable))
    forstr = indt + 'for(auto && {} : {}) {{\n'.format(codegen_node(var, cx), codegen_node(iterable, cx))
    forstr += codegen_block(block, cx.new_scope_context())
    forstr += indt + "}\n"
    return forstr


def codegen_class(node : Call, cx):
    assert isinstance(node, Call)
    name = node.args[0]
    assert isinstance(name, Identifier)
    block = node.args[-1]
    assert isinstance(block, Block)

    indt = cx.indent_str()

    cpp = indt

    cpp += "int x;\n\n"

    defined_interfaces = defaultdict(list)
    local_interfaces = set()

    for b in block.args:
        if isinstance(b, Call) and b.func.name == "def":
            if isinstance(b.declared_type, ColonBinOp):
                return_type, interface_type = b.declared_type.args

                if interface_type.name in defined_interfaces or not any(t == interface_type.name for t in cx.interfaces):
                    defined_interfaces[interface_type.name].append(b)

                cx.interfaces[interface_type.name].append(b)
                local_interfaces.add(interface_type.name)
            cpp += codegen_def(b, cx.new_scope_context())

    interface_def_str = ""
    for interface_type in defined_interfaces:
        interface_def_str += "struct " + str(interface_type) + " : public object {"
        for method in defined_interfaces[interface_type]:
            print("method",method)
            interface_def_str += indt + interface_method_declaration_str(method, cx)
        interface_def_str +=  "};\n\n"

        # interface_cpp = "class "
        #
        # new = RebuiltCall(b.func, b.args)
            # new.parent = b.parent
            # new = build_parents(new)
            # assert isinstance(new.args[-1], Block)
            # needs to build parents: (anyway forget this)
            # new.args[-1].args = [RebuiltCall(func=RebuiltIdentifer("printf"), args=[RebuiltStringLiteral("oh no unimplemented!\n")])]
            # method_declarations.append(codegen_def(new, indent_str))

    def good_but_disable():
        cpp += indt + f"virtual std::shared_ptr<object> operator+(const object & other) const override {{\n"
        # cpp += "    return std::make_shared<Integer>(this->integer + other.integer);\n"
        cpp += indt + f'    printf("adding {name} and object");\n'
        # cpp += indt + "    return *this + other;\n"
        cpp += indt + f"    auto o = dynamic_cast<{name} const*>(&other);"
        cpp += indt + f'    if (!o) {{ printf("damn"); return {{}}; }}'
        cpp += indt + f'    return *this + *o;\n';

        # cpp += indt + "    return other.operator+(*this);\n"
        cpp += indt + "    \n"

        # cpp += indt + "return {};\n"
        cpp += indt + "}\n\n"

        cpp += indt + f"virtual std::shared_ptr<object> operator+(const {name} & other) const {{\n"
        # cpp += "    return std::make_shared<Integer>(this->integer + other.integer);\n"
        # cpp += indt + "    other + *this;\n"
        cpp += indt + f'    printf("adding {name} and {name}");\n'
        cpp += indt + "return {};\n"
        cpp += indt + "}\n\n"
        #
        # cpp += indt + f"virtual std::shared_ptr<object> operator+(const {name} & other) const {{\n"
        # # cpp += "    return std::make_shared<Integer>(this->integer + other.integer);\n"
        # cpp += indt + f'    printf("adding two {name}");\n'
        # cpp += indt + "}"

    cpp += "virtual ~" + str(name) + "() { printf(\"dead %p\\n\", this); }; "

    cpp += indt + "};\n\n"

    if local_interfaces:
        class_header = "struct " + str(name) + " : " + ", ".join([str(i) for i in local_interfaces])
    else:
        class_header = "struct " + str(name) + " : public object"
    class_header += " {\n\n"

    return interface_def_str + class_header + cpp


def codegen_block(block: Block, cx):
    assert isinstance(block, Block)
    assert block.args
    assert not isinstance(block, Module)  # handled elsewhere
    cpp = ""
    indent_str = cx.indent_str()


    for b in block.args:
        if isinstance(b, Identifier) and b.name == "pass":
            cpp += indent_str + "; // pass\n"
            continue
        elif isinstance(b, Call):
            # should still do this (handle non-expr if _statements_ separately)
            # if b.func.name == "if":
            #     cpp += codegen_if(b)

            if b.func.name == "for":
                cpp += codegen_for(b, cx)
                continue
            elif b.func.name == "class":
                cpp += codegen_class(b, cx)
                continue


        cpp += indent_str + codegen_node(b, cx) + ";\n"

    if isinstance(block.parent, Call) and block.parent.func.name == "def":
        last_statement = block.args[-1]

        if not is_return(last_statement):
            cpp += indent_str + "return {};\n"

    return cpp


def interface_method_declaration_str(defnode: Call, cx):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)

    params = []

    assert isinstance(defnode.declared_type, ColonBinOp)
    return_type_node = defnode.declared_type.lhs
    # interface_type_node = defnode.declared_type.rhs

    if return_type_node is None:
        raise CodeGenError("must specify return type of interface method")
    return_type = codegen_type(defnode, return_type_node, cx)

    for i, arg in enumerate(args):
        if arg.declared_type is None:
            raise CodeGenError("parameter types must be specified for interface methods")
        if not isinstance(arg, Identifier):
            raise CodeGenError("Only simple args allowed for interface method (you don't want c++ virtual functions with default arguments)")
        params.append(codegen_type(arg, arg.declared_type, cx) + " " + str(arg))

    return "virtual {} {}({}) = 0;\n\n".format(return_type, name, ", ".join(params))



def codegen_def(defnode: Call, cx):
    assert defnode.func.name == "def"
    name_node = defnode.args[0]
    name = name_node.name
    args = defnode.args[1:]
    block = args.pop()
    assert isinstance(block, Block)

    if isinstance(name_node, Call) and name_node.func.name == "operator" and len(name_node.args) == 1 and isinstance(operator_name_node := name_node.args[0], StringLiteral):
        name = "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else

    if name is None:
        raise CodeGenError(f"can't handle name {name_node} in def {defnode}")

    params = []
    typenames = []

    is_interface_method = isinstance(defnode.declared_type, ColonBinOp)
    if is_interface_method:
        return_type_node = defnode.declared_type.lhs
        interface_type_node = defnode.declared_type.rhs
        assert isinstance(return_type_node, Identifier)
        assert isinstance(interface_type_node, Identifier)
    else:
        return_type_node = defnode.declared_type

    if is_interface_method and return_type_node is None:
        raise CodeGenError("must specify return type of interface method")

    for i, arg in enumerate(args):
        if is_interface_method:
            if arg.declared_type is None:
                raise CodeGenError("parameter types must be specified for interface methods")
            if not isinstance(arg, Identifier):
                raise CodeGenError("Only simple args allowed for interface method (c++ virtual functions with default arguments are best avoided)")

        if arg.declared_type is not None:
            if isinstance(arg, Identifier):
                params.append(codegen_type(arg, arg.declared_type, cx) + " " + str(arg))
            else:
                params.append(codegen_type(arg, arg.declared_type, cx) + " " + codegen_node(arg, cx))
        elif isinstance(arg, Assign) and not isinstance(arg, NamedParameter):
            raise SemanticAnalysisError("Overparenthesized assignments in def parameter lists are not treated as named params. To fix, remove the redundant parenthesese from:", arg)
        elif isinstance(arg, NamedParameter):
            if isinstance(arg.rhs, ListLiteral):
                if isinstance(arg.lhs, Identifier):
                    params.append("std::vector<" + vector_decltype_str(arg, cx) + ">" + str(arg.lhs) + " = {" + ", ".join([codegen_node(a, cx) for a in arg.rhs.args]) + "}")
                else:
                    params.append("std::vector<" + vector_decltype_str(arg, cx) + ">" + codegen_node(arg.lhs, cx) + " = {" + ", ".join([codegen_node(a, cx) for a in arg.rhs.args]) + "}")
                # if arg.rhs.args:
                #     valuepart = "= " + codegen_node(arg.rhs)
                #     declpart = decltype_str(arg.rhs) + " " + codegen_node(arg.lhs)
                # else:
                #     valuepart = ""
                #     declpart = "std::vector<" + decltype_str(arg.rhs) + "> " + codegen_node(arg.lhs)
                #
                # # params.append((decltype_str(arg.rhs) + " " + codegen_node(arg.lhs), "= " + codegen_node(arg.rhs)))
                # params.append((declpart, valuepart))
            elif isinstance(arg.rhs, Call) and arg.rhs.func.name == "lambda":
                params.append("auto " + codegen_node(arg.lhs, cx) + "= " + codegen_node(arg.rhs, cx))
            else:
                if isinstance(arg.lhs, Identifier):
                    params.append(decltype_str(arg.rhs, cx) + " " + str(arg.lhs) + " = " + codegen_node(arg.rhs, cx))
                else:
                    params.append(decltype_str(arg.rhs, cx) + " " + codegen_node(arg.lhs, cx) + " = " + codegen_node(arg.rhs, cx))

        else:
            t = "T" + str(i + 1)
            params.append(t + " " + arg.name)
            typenames.append("typename " + t)

    template = "inline "
    if is_interface_method or name == "main":
        template = ""
    if typenames:
        template = "template <{0}>\n".format(", ".join(typenames))

    if return_type_node is not None:
        # return_type = codegen_type(name_node, name_node.declared_type)
        return_type = codegen_type(defnode, return_type_node, cx)
    elif name == "main":
        return_type = "int"
    else:
        def stop(n):
            return isinstance(n, Block) and n.parent.func.name not in ["if", "while"]

        return_type = "auto"
        found_return = False
        for b in block.args:
            for ret in find_all(b, test=is_return, stop=stop):
                found_return = True
                if is_void_return(ret):
                    # like python treat 'return' as 'return None' (we change the return type of the defined func to allow deduction of type of '{}' by c++ compiler)
                    return_type = 'std::shared_ptr<object>'
                    break

        if not found_return:
            return_type = 'std::shared_ptr<object>'

    # defnode.cpp_return_type = return_type
    funcdef = "{}auto {}({}) -> {}".format(template, name, ", ".join(params), return_type)

    if is_interface_method:
        funcdef += " override" # maybe later: use final if method not 'overridable'

    indt = cx.indent_str()

    return indt + funcdef + " {\n" + codegen_block(block, cx.new_scope_context()) + indt + "}\n\n"


def codegen_lambda(node, cx):
    args = list(node.args)
    block = args.pop()
    assert isinstance(block, Block)
    # params = ["auto " + codegen_node(a) for a in args]
    params = []
    for a in args:
        assert isinstance(a, Identifier)
        params.append("auto " + str(a))
    newcx = cx.new_scope_context()
    return ("[](" + ", ".join(params) + ") {\n" +
            codegen_block(block, newcx) + newcx.indent_str() + "}")


def codegen(expr: Node):
    assert isinstance(expr, Module)
    cx = Context()
    s = codegen_node(expr, cx)
    # s = s.replace("___PLACE_TO_PUT_JUNK", "\n".join(method_declarations))
    print(s)
    s = cpp_preamble + s
    s = s.replace("___PLACE_TO_PUT_JUNK", "")
    return s


# should probably adjust the callers of decltype_str instead of this hackery
class _NoDeclTypeNeeded(Exception):
    def __init__(self, result):
        self.result = result


def decltype_str(node, cx):
    if isinstance(node, ArrayAccess):
        if not isinstance(node.func, Identifier):
            raise CodeGenError("no idea what to do with this indirect array access when printing decltypes")

        for n, c in find_defs(node.func):
            if isinstance(c, Assign):# and hasattr(c.rhs, "_element_decltype_str"):
                if vds := vector_decltype_str(c, cx):
                    return vds
                # return c.rhs._element_decltype_str
            # print("array def", d)

        return "decltype({})::value_type".format(str(node.func))

    # elif isinstance(node, Call) and isinstance(node.func, Identifier) and is_defined_by_class(node.func):
    #     return f"std::declval<std::shared_ptr<{node.func.name}>> ()"

    elif isinstance(node, ListLiteral):
        # never succeeded
        # if not node.args:
        #     if isinstance(node.parent, Assign):
        #         if vds := vector_decltype_str(node.parent):
        #             return vds

        return "std::vector<" + decltype_str(node.args[0], cx) + ">"
        # return vector_decltype_str(node)

        result = "" # "std::vector<"
        end = ">"
        ll = node#.args[0]

        while isinstance(ll, ListLiteral):
            result += "std::vector<" #+ _decltype_str(node.args[0])
            end += ">"
            ll = ll.args[0]

        result += decltype_str(ll)
        result += end

        # if isinstance(node.args[0], ListLiteral):
        #     return "std::vector<" + _decltype_str(node.args[0]) + ">"
        # else:
        #     return "std::vector<" + decltype_str(node.args[0]) + ">"
        return result

    # elif isinstance(node, IntegerLiteral):  # this is nice for readability but not so much debugging output
    #     return "int"

    else:
        try:
            return "decltype({})".format(_decltype_str(node, cx))
        except _NoDeclTypeNeeded as n:
            return n.result


def find_defining_class(node):
    if not isinstance(node, Identifier):
        return None
    for defnode, defcontext in find_defs(node):
        if isinstance(defcontext, Call) and defcontext.func.name == "class":
            class_name = defcontext.args[0]
            assert isinstance(class_name, Identifier)
            return defcontext
    return None


def find_defining_class_of_type(typenode, searchnode):
    # if not isinstance(node, Identifier):
    #     return False
    if res := find_def_starting_from(searchnode, typenode):
        defnode, defcontext = res
        if isinstance(defcontext, Call) and defcontext.func.name == "class":
            class_name = defcontext.args[0]
            assert isinstance(class_name, Identifier)
            return defcontext
    return None


def _decltype_str(node, cx):

    if isinstance(node, IntegerLiteral):
        return str(node)
    elif isinstance(node, StringLiteral):
        # return "std::declval(" + str(node) + "sv" + ")"
        return "std::string {" + str(node) + "}"

    if isinstance(node, BinOp):
        binop = node
        return _decltype_str(binop.lhs, cx) + str(binop.func) + _decltype_str(binop.rhs, cx)
    elif isinstance(node, Call) and isinstance(node.func, Identifier):
        call = node
        # if call.func.name == "lambda":
        #     return codegen_node(call)
        #return codegen_node(call.func) + "(" + ", ".join([_decltype_str(a) for a in call.args]) + ")"

        if class_node := find_defining_class(node.func):
            if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
                result = f"std::unique_ptr<{node.func.name}>"
            else:
                result = f"std::shared_ptr<{node.func.name}>"
            raise _NoDeclTypeNeeded(result)

        return call.func.name + "(" + ", ".join([_decltype_str(a, cx) for a in call.args]) + ")"
    # elif isinstance(node, ArrayAccess):
    #     return "decltype({})::value_type".format(codegen_node(node.func))
        # return "[&](){{ return {}; }}".format(codegen_node(node))
    elif isinstance(node, ListLiteral):
        # if isinstance(node.args[0], ListLiteral):
        #     return "std::vector<" + _decltype_str(node.args[0]) + ">"
        # else:
        #     return "std::vector<" + decltype_str(node.args[0]) + ">"
        return "std::vector<" + decltype_str(node.args[0], cx) + "> {}"
        # return _decltype_str(node.args[0])


    if not isinstance(node, Identifier):
        print("uh oh", node)
        assert 0

    defs = list(find_defs(node))
    if not defs:
        return str(node)

    for def_node, def_context in defs:
        if def_node.declared_type:
            return "std::declval<{}>()".format(codegen_type(def_node, def_node.declared_type, cx))
        if isinstance(def_context, Assign) and def_context.declared_type:
            # return str(def_context.declared_type)
            return "std::declval<{}>()".format(codegen_type(def_context, def_context.declared_type, cx))


    last_ident, last_context = defs[-1]

    # return decltype_str(last_ident)

    if isinstance(last_context, Assign):
        assign = last_context

        return _decltype_str(assign.rhs, cx)

        if isinstance(assign.rhs, BinOp):
            # for arg in assign.rhs.args:
            #     if found := decltype_str(arg):
            #         return found
            binop = assign.rhs
            return decltype_str(binop.lhs) + str(binop.func) + decltype_str(binop.rhs)
        elif isinstance(assign.rhs, Call):
            call = assign.rhs
            return codegen_node(call.func) + "(" + ", ".join([decltype_str(a) for a in call.args]) + ")"
        else:
            print("hmm?1")
            return codegen_node(assign.rhs)
    else:
        print("hmm?2")
        assert 0
        return codegen_node(last_ident)


def vector_decltype_str(node, cx):
    rhs_str = None
    found_use = False

    if isinstance(node, Assign) and isinstance(node.rhs, ListLiteral) and node.rhs.args:
        return decltype_str(node.rhs.args[0], cx)

    for found_use_node in find_uses(node):
        found_use = True
        parent = found_use_node.parent
        while rhs_str is None and not isinstance(parent, Block):
            found_use_context = parent

            if isinstance(found_use_context,
                          AttributeAccess) and found_use_context.lhs is found_use_node and isinstance(
                found_use_context.rhs,
                Call) and found_use_context.rhs.func.name == "append":
                apnd = found_use_context.rhs
                assert len(apnd.args) == 1
                rhs_str = decltype_str(apnd.args[0], cx)

            parent = parent.parent

        if rhs_str is not None:
            break
    if rhs_str is None:
        if found_use:
            # raise CodeGenError("list error, dunno what to do with this:", node)
            print("list error, dunno what to do with this:", node)
        else:
            raise CodeGenError("Unused empty list in template codegen", node)
    return rhs_str


def codegen_type(expr_node, type_node, cx):
    if isinstance(type_node, Identifier):
        name = type_node.name

        # assert isinstance(type_node.parent, ColonBinOp)
        # is_list = isinstance(assign := type_node.parent.parent, Assign) and isinstance(assign.rhs, ListLiteral) or isinstance(assign, ListLiteral)

        if name == "string":
            return "std::string"

        if name == "object":
            return "std::shared_ptr<object>"
        # if name in ["int", "float", "double", "char", "bool"]:
        #     s = name
        # else:

        if name in cx.interfaces:
            name = f"std::shared_ptr<{name}>"
        elif class_node := find_defining_class_of_type(type_node, expr_node):
            if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
                name = f"std::unique_ptr<{name}>"
            else:
                name = f"std::shared_ptr<{name}>"

        if 0 and is_defined_by_class(expr_node):
            assert 0 # are we using this?
            name = f"std::shared_ptr<{name}>"
        else:
            return name

        # return s

        # if is_list:
        #     s = f"std::vector<{s}>"
    return codegen_node(type_node, cx)


def codegen_node(node: Union[Node, Any], cx: typing.Optional[Context] = None):
    cpp = io.StringIO()

    if isinstance(node, Module):
        for modarg in node.args:
            if modarg.func.name == "def":
                defcode = codegen_def(modarg, cx)
                cpp.write(defcode)
            elif modarg.func.name == "class":
                classcode = codegen_class(modarg, cx)
                cpp.write(classcode)
            else:
                print("probably should handle", modarg)
    elif isinstance(node, Call): # not at module level
        if isinstance(node.func, Identifier):
            if node.func.name == "if":
                cpp.write(codegen_if(node, cx))
            elif node.func.name == "def":
                print("need to handle nested def")
            elif node.func.name == "lambda":
                cpp.write(codegen_lambda(node, cx))
            else:
                # if isinstance(node.func, Identifier):

                if class_node := find_defining_class(node.func):
                    if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
                        func_str = f"std::make_unique<{node.func.name}>"
                    else:
                        func_str = "std::make_shared<" + node.func.name + ">"
                else:
                    # we have to avoid codegen_node(node.func) here to avoid wrapping func in a *(get_ptr)  (causes wacky template specialization problems)
                    # # this is not longer the case ^
                    # func_str = node.func.name
                    func_str = codegen_node(node.func, cx)
                # else:
                    # unreachable...
                    # pass

                    # if isinstance(operator_node := node.func, Call) and operator_node.func.name == "operator" and len(operator_node.func.args) == 1 and isinstance(operator_name_node := operator_node.args[0], StringLiteral):
                    #     assert 0
                    #     func_str = "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else
                    # else:
                    #     func_str = codegen_node(node.func)

                func_str += "(" + ", ".join(map(lambda a: codegen_node(a, cx), node.args)) + ")"
                # if is_class:
                #     func_str = "(*get_ptr(" + func_str + "))"

                cpp.write(func_str)
        else:
            # print("need to handle indirect call")

            if isinstance(operator_node := node.func, Call) and operator_node.func.name == "operator" and len(operator_node.args) == 1 and isinstance(operator_name_node := operator_node.args[0], StringLiteral):
                # assert 0
                func_str = "operator" + operator_name_node.func  # TODO fix wonky non-node funcs and args, put raw string somewhere else
                # cpp.write(func_str)
            else:
                func_str = codegen_node(node.func, cx)

            cpp.write(func_str + "(" + ", ".join( map(codegen_node, node.args)) + ")")

    elif isinstance(node, IntegerLiteral):
        cpp.write(str(node))
    elif isinstance(node, Identifier):
        if node.name == "None":
            # cpp.write("(std::shared_ptr<object> ())")
            cpp.write("nullptr")
        elif node.name == "this":
            cpp.write("this")
        #elif not isinstance(node.parent, NamedParameter) and not (isinstance(node.parent, (AttributeAccess) and node.parent.rhs is node):
        # elif not (isinstance(node.parent, (Assign, NamedParameter, AttributeAccess)) and node.parent.rhs is node):

        # this stuff doesn't work with temporaries of various sorts (requires too many checks e.g. am i not a list element etc.
        #elif not (isinstance(node.parent, (Assign, NamedParameter, AttributeAccess))) and not (isinstance(node.parent, Call) and node.parent.func is node):


        #     cpp.write("(*get_ptr(" + node.name + "))")
        else:
            cpp.write(str(node))

    elif isinstance(node, BinOp):

        if isinstance(node, NamedParameter):
            raise SemanticAnalysisError("Unparenthesized assignment treated like named parameter in this context (you need '(' and ')'):", node)

        elif isinstance(node, ColonBinOp):
            assert isinstance(node, SyntaxColonBinOp)  # sanity check type system isn't leaking
            if node.lhs.name == "return":
                cpp.write("return " + codegen_node(node.args[1]))
            else:
                assert False

        elif isinstance(node, Assign) and isinstance(node.lhs, Identifier):
            rhs_str = None

            # Handle template declaration for an empty list by searching for uses
            if isinstance(node.rhs, ListLiteral) and not node.rhs.args:
                rhs_str = "std::vector<" + vector_decltype_str(node, cx) + ">()"

            else:
                rhs_str = codegen_node(node.rhs, cx)

            declared_type = False

            if isinstance(node.lhs, Identifier) and not isinstance(node.rhs, ListLiteral):
                lhs_str = node.lhs.name
                types = [t for t in [node.lhs.declared_type, node.declared_type, node.rhs.declared_type] if t is not None]
                if any(types):
                    assert len(set(types)) == 1
                    lhs_type_str = codegen_type(node.lhs, types[0])
                    # if isinstance(node.rhs, ListLiteral):
                    #     lhs_type_str = f"std::vector::<{lhs_str}>"
                    lhs_str = lhs_type_str + " " + lhs_str
                    declared_type = True
            else:
                lhs_str = codegen_node(node.lhs, cx)

            assign_str = " ".join([lhs_str, node.func, rhs_str])

            if not declared_type and not hasattr(node, "already_declared") and find_def(node.lhs) is None:
                assign_str = "auto " + assign_str

            cpp.write(assign_str)
        else:
            binop_str = None

            separator = " "
            if isinstance(node, AttributeAccess):
                if isinstance(node.lhs, Identifier) and node.lhs.name == "std":
                    return "std::" + codegen_node(node.rhs, cx)

                separator = ""

                if isinstance(node.rhs, Call) and node.rhs.func.name == "append":
                    apnd = node.rhs
                    assert len(apnd.args) == 1

                    is_list = False
                    if isinstance(node.lhs, ListLiteral):
                        is_list = True
                    else:
                        for d in find_defs(node.lhs):
                            # print("found def", d, "when determining if an append is really a push_back")
                            if isinstance(d[1], Assign) and isinstance(d[1].rhs, ListLiteral):
                                is_list = True
                                break
                    if is_list:
                        binop_str = "{}.push_back({})".format(codegen_node(node.lhs, cx), codegen_node(apnd.args[0], cx))

                # elif isinstance(node.rhs, Call) and isinstance(operator_node := node.rhs.func, Call) and operator_node.func.name == "operator" and len(operator_node.args) == 1 and isinstance(operator_name_node := operator_node.args[0], StringLiteral):
                #     binop_str = "(*get_ptr(" + codegen_node(node.lhs) + ")).operator" + operator_name_node.func + "(" + ",".join(codegen_node(a) for a in node.rhs.args) + ")"


            if binop_str is None:

                if isinstance(node, AttributeAccess) :#and node.lhs.name == "this":
                    # don't wrap just 'this' but 'this.foo' gets wrapped

                    if isinstance(node.lhs, Call):
                        if class_node := find_defining_class(node.lhs.func):
                            # template get_ptr stuff (which is a bit dubious taking unique_ptr by reference then taking address...) won't work with a temporary
                            # so detect attribute access of constructor call to class marked unique and print '->' instead
                            if isinstance(class_node.declared_type, Identifier) and class_node.declared_type.name == "unique":
                                return separator.join([codegen_node(node.lhs, cx), "->", codegen_node(node.rhs, cx)])
                    cpp.write("(*get_ptr(" + codegen_node(node.lhs, cx) + "))." + codegen_node(node.rhs, cx))
                else: # (need to wrap indirect attribute accesses): # No need for ^ any more (all identifiers are now wrapped in get_ptr (except non 'class' defined Call funcs)
                    # cpp.write(separator.join([codegen_node(node.lhs), node.func, codegen_node(node.rhs)]))
                    # cpp.write("(*get_ptr(" + codegen_node(node.lhs) + "))" + node.func + "(*get_ptr(" + codegen_node(node.rhs) + "))")  # no matching call to get_ptr for std::endl etc
                    cpp.write(separator.join([codegen_node(node.lhs, cx), node.func, codegen_node(node.rhs, cx)]))
            else:
                cpp.write(binop_str)

    elif isinstance(node, ListLiteral):

        list_type = node.declared_type
        if list_type is None and isinstance(node.parent, Assign):
            list_type = node.parent.declared_type or node.parent.rhs.declared_type or node.parent.lhs.declared_type
        elements = [codegen_node(e, cx) for e in node.args]

        if list_type is not None:
            return "std::vector<{}>{{{}}}".format(codegen_type(node, list_type, cx), ", ".join(elements))
        elif elements:
            return "std::vector<{}>{{{}}}".format(decltype_str(node.args[0], cx), ", ".join(elements))
        else:
            raise CodeGenError("Cannot create vector without elements (in template generation mode)")
    elif isinstance(node, ArrayAccess):
        if len(node.args) > 1:
            raise CodeGenError("advanced slicing not supported yet")
        return codegen_node(node.func, cx) + "[" + codegen_node(node.args[0], cx) + "]"
    elif isinstance(node, CStringLiteral):
        return str(node)
    elif isinstance(node, UnOp):
        opername = node.func
        if opername == ":":
            assert 0
        elif opername == "not":
            return "!" + codegen_node(node.args[0], cx)
        else:
            return "(" + opername + codegen_node(node.args[0], cx) + ")"
    elif isinstance(node, StringLiteral):
        if isinstance(node.parent, Call) and node.parent.func.name in cstdlib_functions:
            # bad idea?: look at the uses of vars defined by string literals, they're const char* if they flow to C lib
            return str(node)  # const char * !
        return "std::string {" + str(node) + "}"
    # elif isinstance(node, RedundantParens):  # too complicated letting codegen deal with this. just disable -Wparens
    #     return "(" + codegen_node(node.args[0]) + ")"

    return cpp.getvalue()

