import typing
from collections import defaultdict
import sys

from .abstractsyntaxtree import Node, Module, Call, Block, UnOp, BinOp, TypeOp, Assign, RedundantParens, Identifier, SyntaxTypeOp, AttributeAccess, ArrayAccess, NamedParameter, TupleLiteral, StringLiteral, Template

from .scope import ClassDefinition, InterfaceDefinition, VariableDefinition, LocalVariableDefinition, GlobalVariableDefinition, ParameterDefinition, FieldDefinition, creates_new_variable_scope, Scope


def isa_or_wrapped(node, NodeClass):
    return isinstance(node, NodeClass) or (isinstance(node, TypeOp) and isinstance(node.args[0], NodeClass))


class IfWrapper:

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))

    def __init__(self, func, args):
        self.func = func
        self._build(args)

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._build(args)

    def _build(self, args):
        # Assumes that func and args have already been processed by `one_liner_expander`
        args = list(args)
        self._args = list(args)
        self.cond = args.pop(0)
        self.thenblock = args.pop(0)
        assert isinstance(self.thenblock, Block)
        self.eliftuples = []
        if args:
            assert len(args) >= 2
            if isinstance(args[-2], Identifier) and args[-2].name == "else":
                self.elseblock = args.pop()
                elseidentifier = args.pop()
                assert isinstance(self.elseblock, Block)
            else:
                self.elseblock = None
            while args:
                elifcond = args.pop(0)
                elifblock = args.pop(0)
                assert isinstance(elifcond, TypeOp)
                assert elifcond.args[0].name == "elif"
                elifcond = elifcond.args[1]
                self.eliftuples.append((elifcond, elifblock))
        else:
            self.elseblock = None


class SemanticAnalysisError(Exception):
    pass


def build_parents(node: Node):

    def visitor(node):
        if isinstance(node, Module):
            node.parent = None
        if not isinstance(node, Node):
            return node
        if not hasattr(node, "name"):
            node.name = None
        rebuilt = []
        for arg in node.args:
            if isinstance(arg, Node):
                arg.parent = node
                arg = visitor(arg)
            rebuilt.append(arg)
        node.args = rebuilt
        if isinstance(node.func, Node):
            node.func.parent = node
            node.func = visitor(node.func)
        if node.declared_type:
            node.declared_type.parent = node
            node.declared_type = visitor(node.declared_type)
        return node
    return visitor(node)


def type_inorder_traversal(typenode: Node, func):
    if isinstance(typenode, TypeOp):
        if not type_inorder_traversal(typenode.lhs, func):
            return False
        if not type_inorder_traversal(typenode.rhs, func):
            return False
        return True
    elif typenode.declared_type is not None:
        temp = typenode.declared_type
        typenode.declared_type = None
        if not type_inorder_traversal(typenode, func):
            typenode.declared_type = temp
            return False
        typenode.declared_type = temp
        if not type_inorder_traversal(typenode.declared_type, func):
            return False
        return True
    else:
        return func(typenode)


def type_node_to_list_of_types(typenode: Node):
    types = []

    if typenode is None:
        return types

    def callback(t):
        types.append(t)
        return True

    type_inorder_traversal(typenode, callback)
    return types


def list_to_typed_node(lst):
    op = None
    first = None
    if not lst:
        return lst
    if len(lst) == 1:
        return lst[0]
    lst = lst.copy()
    while lst:
        second = lst.pop(0)
        if first is None:
            first = second
            second = lst.pop(0)
            op = TypeOp(":", [first, second], first.source)
        else:
            op = TypeOp(":", [op, second], second.source)
    return op


def list_to_attribute_access_node(lst):
    # TODO refactor copied code from above (even better: flatten bin-op args post-parse!)
    op = None
    first = None
    if not lst:
        return lst
    if len(lst) == 1:
        return lst[0]
    lst = lst.copy()
    while lst:
        second = lst.pop(0)
        if first is None:
            first = second
            second = lst.pop(0)
            op = AttributeAccess(".", [first, second], first.source)
        else:
            op = AttributeAccess(".", [op, second], second.source)
    return op


def is_call_lambda(node: Call):
    assert isinstance(node, Call)
    return node.func.name == "lambda" or (isinstance(node.func, ArrayAccess) and node.func.func.name == "lambda")


def build_types(node: Node):

    if not isinstance(node, Node):
        return node

    if isinstance(node, TypeOp) and not isinstance(node, SyntaxTypeOp):
        lhs, rhs = node.args
        # node = build_types(lhs)
        node = lhs
        node.declared_type = rhs  # leaving open possibility this is still a TypeOp
        # node.declared_type = build_types(rhs)

        types = type_node_to_list_of_types(rhs)
        rebuilt = []
        for t in types:
            # we still have cases e.g. lambda with args inside a decltype on rhs of ':' that should build a .declared_type

            # TODO see if this fixed any outstanding issues with nested templates on rhs of operator ':'. Need more testcases but note problems with 'typename assigns' e.g. in def(foo:template<typename:t = typename:blahblah> etc
            t = build_types(t)
            rebuilt.append(t)

        if rebuilt:
            r = list_to_typed_node(rebuilt)
            assert r
            node.declared_type = r

    node.args = [build_types(arg) for arg in node.args]
    node.func = build_types(node.func)
    return node


def one_liner_expander(parsed):

    def ifreplacer(ifop):

        if len(ifop.args) < 1:
            raise SemanticAnalysisError("not enough if args")

        if len(ifop.args) == 1 or not isinstance(ifop.args[1],
                                                 Block):
            if isinstance(ifop.args[0], TypeOp):
                # convert second arg of outermost colon to one element block
                block_arg = ifop.args[0].args[1]
                if isinstance(block_arg, Assign):
                    raise SemanticAnalysisError("no assignment statements in if one liners")
                rebuilt = [ifop.args[0].args[0], Block([block_arg])] + ifop.args[1:]
                return Call(ifop.func, rebuilt, ifop.source)
            else:
                raise SemanticAnalysisError("bad first if-args")

        for i, a in enumerate(list(ifop.args[2:]), start=2):
            if isinstance(a, Block):
                if not (isinstance(ifop.args[i - 1], Identifier) and ifop.args[i - 1].name == "else") and not (isinstance(ifop.args[i - 1], TypeOp) and (isinstance(elifliteral := ifop.args[i - 1].args[0], Identifier) and elifliteral.name == "elif")):
                    raise SemanticAnalysisError(
                        f"Unexpected if arg. Found block at position {i} but it's not preceded by 'else' or 'elif'")
            elif isinstance(a, TypeOp):
                if not a.args[0].name in ["elif", "else"]:
                    raise SemanticAnalysisError(
                        f"Unexpected if arg {a} at position {i}")
                if a.args[0].name == "else":
                    rebuilt = ifop.args[0:i] + [a.args[0], Block([a.args[1]])] + ifop.args[i + 1:]
                    return Call(ifop.func, rebuilt, ifop.source)
                elif a.args[0].name == "elif":
                    if i == len(ifop.args) - 1 or not isinstance(ifop.args[i + 1], Block):
                        c = a.args[1]
                        if not isinstance(c, TypeOp):
                            raise SemanticAnalysisError("bad if args")
                        cond, rest = c.args
                        new_elif = TypeOp(a.op, [a.args[0], cond], a.source)
                        new_block = Block([rest])
                        rebuilt = ifop.args[0:i] + [new_elif, new_block] + ifop.args[i + 1:]
                        return Call(ifop.func, rebuilt, ifop.source)
            elif isinstance(a, Identifier) and a.name == "else":
                if not i == len(ifop.args) - 2:
                    raise SemanticAnalysisError("bad else placement")
                if not isinstance(ifop.args[-1], Block):
                    raise SemanticAnalysisError("bad arg after else")
            else:
                raise SemanticAnalysisError(
                    f"bad if-arg {a} at position {i}")

        return ifop

    def visitor(op):

        if not isinstance(op, Node):
            return op

        if isinstance(op, TypeOp) and not isinstance(op, SyntaxTypeOp) and isinstance(op.args[0], Identifier) and op.args[0].name in ["except", "return", "else", "elif"]:
            op = SyntaxTypeOp(op.op, op.args, op.source)

        if isinstance(op, UnOp) and op.op == "return":
            op = SyntaxTypeOp(":", [Identifier("return", op.source)] + op.args, op.source)

        if isinstance(op, Call):
            if op.func.name == "def":
                if len(op.args) == 0:
                    raise SemanticAnalysisError("empty def")
                # if not isinstance(op.args[0], Identifier):
                #     raise SemanticAnalysisError("bad def args (first arg must be an identifier)")
            elif is_call_lambda(op):
                if not op.args:
                    raise SemanticAnalysisError("not enough lambda args")
            elif op.func.name == "if":
                while True:
                    new = ifreplacer(op)
                    if new is not op:
                        op = new
                        op.is_one_liner_if = True
                    else:
                        break
            # if op.func.name in ["def", "lambda"]:  # no def one liners
            if is_call_lambda(op):
                if not isinstance(op.args[-1], Block):
                    # last arg becomes one-element block
                    op = Call(op.func, op.args[0:-1] + [Block([op.args[-1]])], op.source)
                if is_call_lambda(op):
                    block = op.args[-1]
                    last_statement = block.args[-1]
                    if is_return(last_statement):
                        pass
                    elif isinstance(last_statement, Call) and last_statement.func.name in ["while", "for", "class" "struct"]:
                        synthetic_return = Identifier("return")  # void return
                        block.args += [synthetic_return]
                    else:
                        synthetic_return = SyntaxTypeOp(":", [Identifier("return"), last_statement])
                        if not (isinstance(last_statement, Call) and last_statement.func.name == "lambda"):  # exclude 'lambda' from 'is void?' check
                            synthetic_return.synthetic_lambda_return_lambda = op
                        block.args = block.args[0:-1] + [synthetic_return]
                # if is_return(last_statement):  # Note: this 'is_return' call needs to handle UnOp return (others do not)
                    # if op.func.name == "lambda":
                        # last 'statement' becomes return
                        # block.args = block.args[0:-1] + [SyntaxTypeOp(func=":", args=[RebuiltIdentifer("return"), last_statement])]

                    # else:
                        # We'd like implicit return None like python - but perhaps return 'default value for type' allows more pythonic c++ code
                        # pass # so wait for code generation to 'return {}'
                        # block.args.append(SyntaxTypeOp(func=":", args=[RebuiltIdentifer("return"), RebuiltIdentifer("None")]))

        op.args = [visitor(arg) for arg in op.args]
        op.func = visitor(op.func)
        return op

    return visitor(parsed)


def assign_to_named_parameter(expr):

    def replacer(op):
        if not isinstance(op, Node):
            return op
        if isinstance(op, Call):
            rebuilt = []
            for arg in op.args:
                if isinstance(arg, TypeOp):
                    if isinstance(arg.args[0], Assign):
                        rebuilt.append(TypeOp(arg.op, [NamedParameter(arg.op, arg.args[0].args, arg.source), arg.args[1]], arg.source))
                    else:
                        rebuilt.append(arg)
                elif isinstance(arg, Assign):
                    rebuilt.append(NamedParameter(arg.op, arg.args, arg.source))
                elif isinstance(arg, RedundantParens) and isa_or_wrapped(arg.args[0], Assign):
                    rebuilt.append(arg.args[0])
                else:
                    rebuilt.append(arg)
            op.args = rebuilt

        op.args = [replacer(arg) for arg in op.args]
        return op

    return replacer(expr)


def warn_and_remove_redundant_parens(expr, error=False):

    def replacer(op):
        if isinstance(op, RedundantParens):
            op = op.args[0]
            msg = f"warning: redundant parens {op}"
            if error:
                raise SemanticAnalysisError(msg)
            else:
                print(msg, file=sys.stderr)
        if not isinstance(op, Node):
            return op
        op.args = [replacer(arg) for arg in op.args]
        op.func = replacer(op.func)
        return op

    return replacer(expr)


def is_return(node):
    return ((isinstance(node, TypeOp) and node.lhs.name == "return") or (
            isinstance(node, Identifier) and node.name == "return") or (
            isinstance(node, UnOp) and node.op == "return"))


# whatever 'void' means - but syntactically this is 'return' (just an identifier)
# (NOTE: requires prior replacing of UnOp return)
def is_void_return(node):
    return not isinstance(node, TypeOp) and is_return(node) and not (isinstance(node.parent, TypeOp) and node.parent.lhs is node)


# find closest following use
def find_use(assign: Assign):
    assert isinstance(assign, Assign)
    if isinstance(assign.parent, Block):
        index = assign.parent.args.index(assign)
        following = assign.parent.args[index + 1:]
        for f in following:
            if isinstance(assign.lhs, Identifier) and assign.lhs.name == f:
                return f, f
            else:
                for a in f.args:
                    if isinstance(assign.lhs, Identifier) and assign.lhs.name == a.name:
                        return a, f
    return None


def find_all(node: Node, test=lambda n: False, stop=lambda n: False):
    assert isinstance(node, Node)

    if stop(node):
        return
    if test(node):
        yield node

    for arg in node.args:
        if stop(arg):
            return
        yield from find_all(arg, test=test, stop=stop)
    if node.func:
        yield from find_all(node.func, test=test, stop=stop)


def find_nodes(node, search_node):
    assert isinstance(node, Node)
    if not isinstance(search_node, Node):
        return None
    if node.name == search_node.name:
        yield search_node
    else:
        for arg in search_node.args:
            yield from find_nodes(node, arg)
        yield from find_nodes(node, search_node.func)


def find_uses(node):
    return _find_uses(node, node)


def _find_uses(node, search_node):
    # assert isinstance(node, Assign)
    if not isinstance(node, Assign):
        return
    assign = node

    if isinstance(search_node, Identifier) and assign.lhs.name == search_node.name:
        return (yield search_node)

    if isinstance(search_node.parent, Call) and search_node.parent.func.name in ["def", "lambda"]:
        block = search_node.parent.args[-1]
        assert isinstance(block, Block)
        for f in block.args:
            # if isinstance(assign.lhs, Identifier) and assign.lhs.name == f:
            #     return f, f
            yield from find_nodes(assign.lhs, f)

    elif isinstance(search_node.parent, Block):
        index = search_node.parent.args.index(search_node)
        following = search_node.parent.args[index + 1:]
        for f in following:
            # if isinstance(assign.lhs, Identifier) and assign.lhs.name == f:
            #     return f, f
            yield from find_nodes(assign.lhs, f)
    else:
        for a in search_node.args:
            yield from find_nodes(assign.lhs, a)
        yield from find_nodes(assign.lhs, search_node.func)


def is_def_or_class_like(call : Call):
    assert isinstance(call, Call)
    if call.func.name in ["def", "lambda", "class", "struct"]:
        return True
    if isinstance(call.func, ArrayAccess) and call.func.func.name == "lambda":
        # lambda with explicit capture list
        return True
    return False


class ScopeVisitor:
    def __init__(self):
        self._module_scope = None

    def visit_Node(self, node):
        if node.scope is None:
            node.scope = node.parent.scope

    def visit_Call(self, call):
        self.visit_Node(call)

        # TODO we should be handling class definitions here (this will allow us
        # to stop hackily inserting the args of an included module into the includee)
        # plus something like this:
        #if call.func.name == "include":
        #    assert isinstance(call.args[1], Module)
        #    call.args[1].scope = call.scope
        #    return

        if is_def_or_class_like(call):
            # call.scope = call.scope.enter_scope()
            call_inner_scope = call.scope.enter_scope()

        for a in call.args:
            # TODO these kind of decisions should be controlled by built-in language constructs
            # for use by macros / custom special-form calls. Something like e.g. localscope and even
            # block_ancestor_scope (scope_with_next_block_in_child_scope ?) etc

            if isinstance(a, Block) and not is_def_or_class_like(call):
                index = call.args.index(a)
                if index > 0:
                    # e.g. the "then" block of an if-stmt is a child scope of the if-condition scope
                    a.scope = call.args[index - 1].scope.enter_scope()
                else:
                    a.scope = call.scope.enter_scope()
            elif call.func.name in ["if", "for", "while"]:
                a.scope = call.scope.enter_scope()
            elif is_def_or_class_like(call):
                a.scope = call_inner_scope

            if isinstance(a, Identifier) and call.func.name in ["def", "lambda"]: #is_def_or_class_like(call):
                a.scope.add_variable_definition(defined_node=a, defining_node=call)
                # note that default parameters handled as generic Assign
            elif isinstance(a, TypeOp) and is_def_or_class_like(call):
                # lambda inside a decltype itself a .declared_type case
                assert 0, "should be unreachable"
                assert call.func.name == "lambda", "unexpected non-lowered ast TypeOf node"
                a.scope.add_variable_definition(defined_node=a.lhs, defining_node=call)

            elif isinstance(a, BinOp) and a.op == "in" and call.func.name == "for":
                if isinstance(a.lhs, Identifier):
                    a.scope.add_variable_definition(defined_node=a.lhs, defining_node=call)
                elif isinstance(a.lhs, TupleLiteral):
                    for tuple_arg in a.lhs.args:
                        a.scope.add_variable_definition(defined_node=tuple_arg, defining_node=call)

    # def visit_Block(self, block):
    #     block.scope = block.scope.enter_scope()
    #     return block

    def visit_Identifier(self, ident):
        self.visit_Node(ident)
        if ident.declared_type and not isinstance(ident.parent, Template) and not ident.declared_type.name in ["using", "namespace", "typedef"] :
            ident.scope.add_variable_definition(defined_node=ident, defining_node=ident)

    def visit_Assign(self, assign):
        self.visit_Node(assign)
        if isinstance(assign.lhs, Identifier) and not (assign.lhs.declared_type and assign.lhs.declared_type.name in ["using", "namespace"]):
            assign.scope.add_variable_definition(defined_node=assign.lhs, defining_node=assign)
        elif isinstance(assign.lhs, TupleLiteral):
            for a in assign.lhs.args:
                if isinstance(a, Identifier):
                    assign.scope.add_variable_definition(defined_node=a, defining_node=assign)

    def visit_Module(self, module):
        if module.scope:
            # embedded module (from include) already handled
            return
        module.scope = Scope()
        self._module_scope = module.scope


def apply_replacers(module: Module, visitors):

    def replace(node):

        if not isinstance(node, Node):
            return node

        for v in visitors:
            func_name = "visit_" + node.__class__.__name__
            new = None
            if hasattr(v, func_name):
                new = getattr(v, func_name)(node)
            elif hasattr(v, "visit_Node"):
                new = v.visit_Node(node)
            if new is not None:
                node = new

        node.args = [replace(a) for a in node.args]
        node.func = replace(node.func)
        node.declared_type = replace(node.declared_type)
        return node

    return replace(module)


def semantic_analysis(expr: Module):
    assert isinstance(expr, Module) # enforced by parser

    expr = one_liner_expander(expr)
    expr = assign_to_named_parameter(expr)
    expr = warn_and_remove_redundant_parens(expr)

    expr = build_types(expr)
    expr = build_parents(expr)
    expr = apply_replacers(expr, [ScopeVisitor()])

    print("after lowering", expr)

    def defs(node):
        if not isinstance(node, Node):
            return

        x = node.scope.find_def(node)
        if x:
            print("found def", node, x)
        else:
            pass
            # print("no def for", node)

        for u in find_uses(node):
            print("found use ", node, u, u.parent, u.parent.parent)

        d = list(node.scope.find_defs(node))
        if d:
            print("defs list ", node, d)
        for a in node.args:
            defs(a)
            defs(a.func)

    defs(expr)

    return expr
