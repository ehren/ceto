from parser import Node, Module, Call, Block, UnOp, BinOp, ColonBinOp, Assign, RedundantParens, Identifier, IntegerLiteral, RebuiltColon, SyntaxColonBinOp
import sys

def isa_or_wrapped(node, NodeClass):
    return isinstance(node, NodeClass) or (isinstance(node, ColonBinOp) and isinstance(node.args[0], NodeClass))


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
        self.func = "NamedParameter"
        self.args = args  # [lhs, rhs]

    def __repr__(self):
        return "{}({})".format(self.func, ",".join(map(str, self.args)))


# should be renamed "IfWrapper"
class IfNode:#(Call):  # just a helper class for now (avoid adding to ast)

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
        self._args = list(args)
        self.cond = args.pop(0)
        self.thenblock = args.pop(0)
        assert isinstance(self.thenblock, Block)
        self.eliftuples = []
        if args:
            self.elseblock = args.pop()
            elseidentifier = args.pop()
            assert isinstance(elseidentifier, Identifier) and elseidentifier.name == "else"
            while args:
                elifcond = args.pop(0)
                elifblock = args.pop(0)
                assert isinstance(elifcond, ColonBinOp)
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

        if isinstance(node, ColonBinOp) and not isinstance(node, SyntaxColonBinOp):
            lhs, rhs = node.args
            node = lhs
            node.declared_type = rhs  # leaving open possibility this is still a ColonBinOp

        node.args = [visitor(arg) for arg in node.args]
        return node

    return visitor(node)


def one_liner_expander(parsed):

    def ifreplacer(ifop):

        if len(ifop.args) < 1:
            raise SemanticAnalysisError("not enough if args")

        if len(ifop.args) == 1 or not isinstance(ifop.args[1],
                                                 Block):
            if isinstance(ifop.args[0], ColonBinOp):
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
                if not (isinstance(ifop.args[i - 1], Identifier) and ifop.args[i - 1].name == "else") and not (isinstance(ifop.args[i - 1], ColonBinOp) and (isinstance(elifliteral := ifop.args[i - 1].args[0], Identifier) and elifliteral.name == "elif")):
                    raise SemanticAnalysisError(
                        f"Unexpected if arg. Found block at position {i} but it's not preceded by 'else' or 'elif'")
            elif isinstance(a, ColonBinOp):
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
                        if not isinstance(c, ColonBinOp):
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

        if isinstance(op, ColonBinOp) and not isinstance(op, SyntaxColonBinOp) and isinstance(op.args[0], Identifier) and op.args[0].name in ["except", "return", "else", "elif"]:
            op = SyntaxColonBinOp(op.func, op.args)

        if isinstance(op, UnOp) and op.func == "return":
            op = SyntaxColonBinOp(func=":", args=[RebuiltIdentifer("return")] + op.args)

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
                if op.func.name in ["def", "lambda"]:
                    if not isinstance(op.args[-1], Block):
                        # last arg becomes one-element block
                        op = RebuiltCall(func=op.func, args=op.args[0:-1] + [RebuiltBlock(args=[op.args[-1]])])
                    if op.func.name == "lambda":
                        block = op.args[-1]
                        last_statement = block.args[-1]
                        if not is_return(last_statement):
                            block.args = block.args[0:-1] + [SyntaxColonBinOp(func=":", args=[RebuiltIdentifer("return"), last_statement])]
                    # if is_return(last_statement):  # Note: this 'is_return' call needs to handle UnOp return (others do not)
                        # if op.func.name == "lambda":
                            # last 'statement' becomes return
                            # block.args = block.args[0:-1] + [SyntaxColonBinOp(func=":", args=[RebuiltIdentifer("return"), last_statement])]

                        # else:
                            # We'd like implicit return None like python - but perhaps return 'default value for type' allows more pythonic c++ code
                            # pass # so wait for code generation to 'return {}'
                            # block.args.append(SyntaxColonBinOp(func=":", args=[RebuiltIdentifer("return"), RebuiltIdentifer("None")]))

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
                if isinstance(arg, ColonBinOp):
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
        if isinstance(r, Call) and r.func.name == "class":
            class_name = r.args[0]
            if isinstance(class_name, Identifier) and class_name.name == node_to_find.name and class_name is not node_to_find:
                return class_name, r
        else:
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
        for r in reversed(preceding):
            # if isinstance(r, Assign) and isinstance(r.lhs, Identifier) and r.lhs.name == node_to_find.name:
            #     return r.lhs, r
            f = _find_assign(r, node_to_find)
            if f is not None:
                return f

        # call = parent.parent
        # assert isinstance(call, Call)
        # for a in call.args:
        #     if a.name == node_to_find.name:
        #         return a, call

        return _find_def(parent.parent, parent, node_to_find)
    elif isinstance(parent, Call):
        if parent.func.name == "def":
            # should handle the def of the function name.... (or not?)

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


def find_def_starting_from(search_node, node_to_find):
    res = _find_def(search_node.parent, search_node, node_to_find)
    return res


def is_return(node):
    return ((isinstance(node, ColonBinOp) and node.lhs.name == "return") or (
            isinstance(node, Identifier) and node.name == "return") or (
            isinstance(node, UnOp) and node.func == "return"))


# whatever 'void' means - but syntactically this is 'return' (just an identifier)
# (NOTE: requires prior replacing of UnOp return)
def is_void_return(node):
    return not isinstance(node, ColonBinOp) and is_return(node) and not (isinstance(node.parent, ColonBinOp) and node.parent.lhs is node)


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
    if test(node):
        yield node
    if stop(node):
        return

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


def semantic_analysis(expr: Module):
    assert isinstance(expr, Module) # enforced by parser

    expr = one_liner_expander(expr)
    expr = assign_to_named_parameter(expr)
    expr = warn_and_remove_redundant_parens(expr)

    expr = build_types(expr)
    expr = build_parents(expr)

    print("after lowering", expr)

    def defs(node):
        if not isinstance(node, Node):
            return

        x = find_def(node)
        if x:
            print("found def", node, x)
        else:
            pass
            # print("no def for", node)

        for u in find_uses(node):
            print("found use ", node, u, u.parent, u.parent.parent)

        d = list(find_defs(node))
        if d:
            print("defs list ", node, d)

        for a in node.args:
            defs(a)
            defs(a.func)

    defs(expr)

    return expr
