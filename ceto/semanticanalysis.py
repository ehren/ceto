import typing
from collections import defaultdict

from parser import Node, Module, Call, Block, UnOp, BinOp, TypeOp, Assign, RedundantParens, Identifier, IntegerLiteral, RebuiltColon, SyntaxTypeOp
import sys

def isa_or_wrapped(node, NodeClass):
    return isinstance(node, NodeClass) or (isinstance(node, TypeOp) and isinstance(node.args[0], NodeClass))


class RebuiltIdentifer(Identifier):
    def __init__(self, name):
        self.func = name
        self.args = []
        self.name = name


class RebuiltBlock(Block):

    def __init__(self, args):
        self.func = "Block"
        self.args = args


class RebuiltCall(Call):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class RebuiltAssign(Assign):
    def __init__(self, args):
        self.func = "Assign"
        self.args = args


class NamedParameter(Assign):
    def __init__(self, args):
        # self.func = "NamedParameter"
        self.func = "="  # paper over that we've further loosened named parameter vs assignment distinction in codegen
        self.args = args

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


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
        return node
    return visitor(node)


def build_types(node: Node):

    def visitor(node):
        if not isinstance(node, Node):
            return node

        if isinstance(node, TypeOp) and not isinstance(node, SyntaxTypeOp):
            lhs, rhs = node.args
            # node = visitor(lhs)
            node = lhs
            node.declared_type = rhs  # leaving open possibility this is still a TypeOp
            # node.declared_type = visitor(rhs)

        node.args = [visitor(arg) for arg in node.args]
        node.func = visitor(node.func)
        return node

    return visitor(node)


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
                rebuilt = [ifop.args[0].args[0], RebuiltBlock(args=[block_arg])] + ifop.args[1:]
                return RebuiltCall(func=ifop.func, args=rebuilt)
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
                    rebuilt = ifop.args[0:i] + [a.args[0], RebuiltBlock(
                        args=[a.args[1]])] + ifop.args[i + 1:]
                    return RebuiltCall(ifop.func, args=rebuilt)
                elif a.args[0].name == "elif":
                    if i == len(ifop.args) - 1 or not isinstance(ifop.args[i + 1], Block):
                        c = a.args[1]
                        if not isinstance(c, TypeOp):
                            raise SemanticAnalysisError("bad if args")
                        cond, rest = c.args
                        new_elif = RebuiltColon(a.func, [a.args[0], cond])
                        new_block = RebuiltBlock(args=[rest])
                        rebuilt = ifop.args[0:i] + [new_elif, new_block] + ifop.args[i + 1:]
                        return RebuiltCall(ifop.func, args=rebuilt)
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
            op = SyntaxTypeOp(op.func, op.args)

        if isinstance(op, UnOp) and op.func == "return":
            op = SyntaxTypeOp(func=":", args=[RebuiltIdentifer("return")] + op.args)

        if isinstance(op, Call):
            if isinstance(op.func, Identifier):
                if op.func.name == "def":
                    if len(op.args) < 2:
                        raise SemanticAnalysisError("not enough def args")
                    # if not isinstance(op.args[0], Identifier):
                    #     raise SemanticAnalysisError("bad def args (first arg must be an identifier)")
                elif op.func.name == "lambda":
                    if not op.args:
                        raise SemanticAnalysisError("not enough lambda args")
                elif op.func.name == "if":
                    while True:
                        new = ifreplacer(op)
                        if new is not op:
                            op = new
                        else:
                            break
                # if op.func.name in ["def", "lambda"]:  # no def one liners
                if op.func.name == "lambda":
                    if not isinstance(op.args[-1], Block):
                        # last arg becomes one-element block
                        op = RebuiltCall(func=op.func, args=op.args[0:-1] + [RebuiltBlock(args=[op.args[-1]])])
                    if op.func.name == "lambda":
                        block = op.args[-1]
                        last_statement = block.args[-1]
                        if is_return(last_statement):
                            pass
                        elif isinstance(last_statement, Call) and last_statement.func.name in ["while", "for", "class"]:
                            synthetic_return = RebuiltIdentifer("return")
                            block.args += [synthetic_return]
                        else:
                            synthetic_return = SyntaxTypeOp(func=":", args=[RebuiltIdentifer("return"), last_statement])
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
                        rebuilt.append(RebuiltColon(func=arg.func, args=[NamedParameter(args=arg.args[0].args), arg.args[1]]))
                    else:
                        rebuilt.append(arg)
                elif isinstance(arg, Assign):
                    rebuilt.append(NamedParameter(args=arg.args))
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


def _find_def(parent, child, node_to_find):
    def _find_assign(r, node_to_find):
        if not isinstance(r, Node):
            return None
        if isinstance(r, Block):
            return None
        if isinstance(r, Assign) and isinstance(r.lhs, Identifier) and r.lhs.name == node_to_find.name and r.lhs is not node_to_find:
            return r.lhs, r
        if isinstance(r, Call):
            call_func_name = r.func.name
            if call_func_name == "class":
                class_name = r.args[0]
                if isinstance(class_name, Identifier) and class_name.name == node_to_find.name and class_name is not node_to_find:
                    return class_name, r
            # elif call_func_name == "for":
            #     instmt = r.args[0]
            #     if isinstance(instmt, BinOp) and instmt.func == "in":
            #         itervar = instmt.args[0]
            #         if isinstance(itervar, Identifier) and itervar.name == node_to_find.name:
            #             return itervar, r
        for a in r.args:
            if f := _find_assign(a, node_to_find):
                return f
        return None

    if parent is None:
        return None
    if not isinstance(node_to_find, Identifier):
        return None
    if not isinstance(node_to_find, Node):
        return None
    # if isinstance(parent, Module):
    #
    #     # need to handle this like a block
    #
    #     return None
    elif isinstance(parent, Block):
        index = parent.args.index(child)
        preceding = parent.args[0:index]

        if isinstance(parent.parent, Call) and parent.parent.func.name == "if":
            for i, ifarg in enumerate(parent.parent.args):
                if parent is ifarg:
                    assert i > 0
                    testexpr = parent.parent.args[i - 1]
                    assert not isinstance(testexpr, Block)
                    preceding.insert(0, testexpr)

        for r in reversed(preceding):
            # if isinstance(r, Assign) and isinstance(r.lhs, Identifier) and r.lhs.name == node_to_find.name:
            #     return r.lhs, r
            f = _find_assign(r, node_to_find)
            if f is not None:
                return f
            if isinstance(r, Identifier) and r.declared_type is not None and r.name == node_to_find.name:
                # treat declarations of block-level locals (which require a type!) like defs. TODO: There may be places in codegen that improperly ignore such a def (expecting an assignment) e.g. typed list declarations
                return r, r

        # call = parent.parent
        # assert isinstance(call, Call)
        # for a in call.args:
        #     if a.name == node_to_find.name:
        #         return a, call

        return _find_def(parent.parent, parent, node_to_find)
    elif isinstance(parent, Call):
        if parent.func.name in ["def", "lambda"]:
            for callarg in parent.args:
                if callarg.name == node_to_find.name and callarg is not node_to_find:
                    return callarg, parent
                elif isinstance(callarg, NamedParameter) and callarg.lhs.name == node_to_find.name:
                    return callarg.lhs, callarg
        elif parent.func.name == "class":
            class_name = parent.args[0]
            if isinstance(class_name, Identifier) and class_name.name == node_to_find.name and class_name is not node_to_find:
                # assert 0
                print("why was this commented out?")
                return class_name, parent
        elif parent.func.name == "for":
            instmt = parent.args[0]
            if isinstance(instmt, BinOp) and instmt.func == "in":
                itervar = instmt.args[0]
                if isinstance(itervar, Identifier) and itervar.name == node_to_find.name:
                    return itervar, parent
            else:
                assert 0 # remove when func str fixed

        return _find_def(parent.parent, parent, node_to_find)
    elif isinstance(parent, Assign) and parent.lhs.name == node_to_find.name and parent.lhs is not node_to_find:
        return parent.lhs, parent
    else:
        return _find_def(parent.parent, parent, node_to_find)


# find closest preceding def
def find_def(node):
    if not isinstance(node, Node):
        return None
    res = _find_def(node.parent, node, node)
    return res


def is_return(node):
    return ((isinstance(node, TypeOp) and node.lhs.name == "return") or (
            isinstance(node, Identifier) and node.name == "return") or (
            isinstance(node, UnOp) and node.func == "return"))


# whatever 'void' means - but syntactically this is 'return' (just an identifier)
# (NOTE: requires prior replacing of UnOp return)
def is_void_return(node):
    return not isinstance(node, TypeOp) and is_return(node) and not (isinstance(node.parent, TypeOp) and node.parent.lhs is node)


def find_defs(node):

    found = find_def(node)

    if found is not None:
        yield found

        found_node, found_context = found
        if isinstance(found_context, Assign):
            if isinstance(found_context.rhs, Identifier):
                yield from find_defs(found_context.rhs)
            else:
                print("stopping at complex definition")
        else:
            print("are we handling this correctly? (def args)", found_node, found_context)


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


def find_all(node, test=lambda n: False, stop=lambda n: False):
    if not isinstance(node, Node):
        return
    if stop(node):
        return
    if test(node):
        yield node

    for arg in node.args:
        if stop(arg):
            return
        yield from find_all(arg, test)
    yield from find_all(node.func, test)


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


def build_types(node: Node):

    def visitor(node):
        if not isinstance(node, Node):
            return node

        if isinstance(node, TypeOp) and not isinstance(node, SyntaxTypeOp):
            lhs, rhs = node.args
            # node = visitor(lhs)
            node = lhs
            node.declared_type = rhs  # leaving open possibility this is still a TypeOp
            # node.declared_type = visitor(rhs)

        node.args = [visitor(arg) for arg in node.args]
        node.func = visitor(node.func)
        return node

    return visitor(node)


class ClassDefinition:

    def __init__(self, name_node : Identifier, class_def_node: Call, is_generic_param_index, is_unique):
        self.name_node = name_node
        self.class_def_node = class_def_node
        self.is_generic_param_index = is_generic_param_index
        self.is_unique = is_unique

    def has_generic_params(self):
        return True in self.is_generic_param_index.values()


class InterfaceDefinition(ClassDefinition):
    def __init__(self):
        pass


class VariableDefinition:

    def __init__(self, defined_node: Identifier, defining_node: Node):
        self.defined_node = defined_node
        self.defining_node = defining_node


class Scope:

    def __init__(self):
        self.interfaces = defaultdict(list)
        self.class_definitions = []
        self.variable_definitions = []
        self.indent = 0
        self.parent : Scope = None
        self.in_function_body = False
        self.in_function_param_list = False  # TODO unused remove
        self.in_class_body = False
        self.in_decltype = False

    def indent_str(self):
        return "    " * self.indent

    def lookup_class(self, class_node) -> typing.Optional[ClassDefinition]:
        if not isinstance(class_node, Identifier):
            return None
        for c in self.class_definitions:
            if isinstance(c.name_node, Identifier) and c.name_node.name == class_node.name:
                return c
        if class_node.name in self.interfaces:
            return InterfaceDefinition()
        if self.parent:
            return self.parent.lookup_class(class_node)
        return None

    def find_defs(self, var_node):
        if not isinstance(var_node, Identifier):
            return

        for d in self.variable_definitions:
            if d.defined_node.name == var_node.name:
                yield d.defined_node, d.defining_node
                if isinstance(d.defining_node, Assign) and isinstance(d.defining_node.rhs, Identifier):
                    yield from self.find_defs(d.defining_node.rhs)

        if self.parent is not None:
            yield from self.parent.find_defs(var_node)

    def enter_scope(self):
        s = Scope()
        s.parent = self
        s.in_function_body = self.in_function_body
        s.in_decltype = self.in_decltype
        s.indent = self.indent + 1
        return s


class ScopeVisitor:

    def visit_Node(self, node):
        if not hasattr(node, "scope"):
            node.scope = node.parent.scope
        return node

    def visit_Call(self, call):
        call = self.visit_Node(call)

        scope = call.scope
        if call.func.name in ["def", "lambda", "class", "while", "for"]:
            scope = scope.enter_scope()

        for a in call.args:
            a.scope = scope

            if isinstance(a, Block):
                a.scope = a.scope.enter_scope()

            elif isinstance(a, BinOp) and a.func == "in" and call.func.name == "for" and isinstance(a.lhs, Identifier):
                a.scope.variable_definitions.append(
                    VariableDefinition(defined_node=a.lhs,
                                       defining_node=call))

        return call

    def visit_Identifier(self, ident):
        ident = self.visit_Node(ident)
        if ident.declared_type:
            ident.scope.variable_definitions.append(VariableDefinition(defined_node=ident, defining_node=ident))
        return ident

    def visit_Assign(self, assign):
        assign = self.visit_Node(assign)
        if isinstance(assign.lhs, Identifier):
            assign.scope.variable_definitions.append(VariableDefinition(defined_node=assign.lhs, defining_node=assign))
        return assign

    def visit_Module(self, module):
        module.scope = Scope()
        return module


def apply_visitors(module: Module, visitors):

    def _visit(node):

        if not isinstance(node, Node):
            return node

        for v in visitors:
            func_name = "visit_" + node.__class__.__name__
            if hasattr(v, func_name):
                node = getattr(v, func_name)(node)
            else:
                node = v.visit_Node(node)

        node.args = [_visit(a) for a in node.args]
        node.func = _visit(node.func)
        return node

    return _visit(module)


def semantic_analysis(expr: Module):
    assert isinstance(expr, Module) # enforced by parser

    expr = one_liner_expander(expr)
    expr = assign_to_named_parameter(expr)
    expr = warn_and_remove_redundant_parens(expr)

    expr = build_types(expr)
    expr = build_parents(expr)
    expr = apply_visitors(expr, [ScopeVisitor()])

    print("after lowering", expr)

    def defs(node):
        if not isinstance(node, Node):
            return

        x = find_def(node)
        x2 = node.scope.find_defs(node)
        if x:
            print("found def", node, x, x2)
        else:
            pass
            # print("no def for", node)

        for u in find_uses(node):
            print("found use ", node, u, u.parent, u.parent.parent)

        d = list(find_defs(node))
        d2 = list(node.scope.find_defs(node))
        if d:
            print("defs list ", node, d, d2)
        if d != d2:
            print("maybe a prob")
        for a in node.args:
            defs(a)
            defs(a.func)

    defs(expr)

    return expr


