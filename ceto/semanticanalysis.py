import typing
from collections import defaultdict
import sys
import os
import subprocess
import concurrent.futures
import shutil

from .abstractsyntaxtree import *#Node, Module, Call, Block, UnOp, BinOp, TypeOp, Assign, RedundantParens, Identifier, SyntaxTypeOp, AttributeAccess, ArrayAccess, NamedParameter, TupleLiteral, StringLiteral, Template

from .scope import ClassDefinition, InterfaceDefinition, VariableDefinition, LocalVariableDefinition, GlobalVariableDefinition, ParameterDefinition, FieldDefinition, FunctionDefinition, creates_new_variable_scope, Scope, comes_before

# from ._abstractsyntaxtree import visit_macro_definitions, MacroDefinition, MacroScope
# from ._abstractsyntaxtree import macro_matches, macro_trampoline

from ._abstractsyntaxtree import MacroDefinition, expand_macros

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



def _ban_references_lambda(node):
#    code = """(lambda[ref] (:
#    static_assert(not std::is_reference_v<decltype(ceto_private_placeholder)>)
#    return ceto_private_placeholder
#):decltype(auto))()"""

#    from .parser import parse
#    ban_references_lambda = parse(code).args[0]
#    print(ban_references_lambda.ast_repr(ceto_evalable=False, preserve_source_loc=False))
#    import sys
#    sys.exit(-1)

    clone = node.clone()

    ban_references_lambda = Call(TypeOp(":", [Call(ArrayAccess(Identifier("lambda", ), [Identifier("ref", ), ], ), [Block([Call(Identifier("static_assert", ), [UnOp("not", [ScopeResolution("::", [Identifier("std", ), Template(Identifier("is_reference_v", ), [Call(Identifier("overparenthesized_decltype", ), [clone, ], ), ], ), ], )], ), ], ), SyntaxTypeOp(":", [Identifier("return"), node], ), ], ), ], ), Call(Identifier("decltype", ), [Identifier("auto", ), ], ), ], ), [], )

    #ban_references_lambda = Call(Identifier("CETO_BAN_REFS"), [node])

    ban_references_lambda.parent = node.parent
    node.parent = ban_references_lambda
    clone.parent = ban_references_lambda
    clone.scope = node.scope
    ban_references_lambda.scope = node.scope
    #ban_references_lambda = basic_semantic_analysis(ban_references_lambda)

    return ban_references_lambda


def safety_checks(node):

    #from ceto.compiler import cmdargs
    #if not cmdargs._norefs:
    #    return node

    if isinstance(node, Call) and node.func.name == "for":

        # https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2012r0.pdf

        if len(node.args) != 2:
            raise SemanticAnalysisError("unexpected number of for args", node)
        if not isinstance(node.args[1], Block):
            raise SemanticAnalysisError("2nd for arg must be a Block", node)
        #new_for = Call(Identifier("for"), node.args)
        #return new_for

        in_expr = node.args[0]
        if not (isinstance(in_expr, BinOp) and in_expr.op == "in"):
            raise SemanticAnalysisError("expected 'in' expression as first arg to 'for'", node)

        iterable = in_expr.rhs
        iter_var = in_expr.lhs
        for_body = node.args[1]

        if isinstance(iterable, Identifier) and any(find_all(for_body, lambda n: n.name == iterable.name)):
            raise SemanticAnalysisError("you may not refer to the iterable in the body of a for loop!", iterable)
        elif isinstance(iterable, AttributeAccess) and isinstance(iterable.lhs, Identifier):

            for_scope = node.parent.scope

            is_over_self = iterable.lhs.name == "self"
            is_over_local_not_aliasing_self = False
            aliased_locals = []
            if not is_over_self:
                is_over_local_not_aliasing_self = True

                for defn in for_scope.find_defs(iterable.lhs):
                    if isinstance(defn, ParameterDefinition):
                        is_over_local_not_aliasing_self = False
                        break
                    elif isinstance(defn, LocalVariableDefinition): # and rhs of defining assignment doesn't alias self
                        aliased_locals.append(defn.defined_node)

                        to_check = [defn.defining_node]
                        while to_check:
                            check = to_check.pop()

                            def is_local(n):
                                localdef = n.scope.find_def(n)
                                if isinstance(localdef, LocalVariableDefinition):
                                    aliased_locals.append(localdef.defined_node)
                                    check.append(localdef.defining_node)
                                elif isinstance(localdef, ParameterDefinition):
                                    nonlocal is_over_local_not_aliasing_self
                                    is_over_local_not_aliasing_self = False

                            find_all(check, is_local)

                            if not is_over_local_not_aliasing_self:
                                break

            def is_acceptable_use_of_self_this(n):
                assert n.name in ("this", "self")
                assert is_over_self
                if isinstance(n.parent, AttributeAccess) and n.parent.lhs is n and not (
                     isinstance(n.parent.parent, Call) and n.parent is n.parent.parent.func
                   ) and isinstance(n.parent.rhs, Identifier) and isinstance(iterable.rhs, Identifier) and n.parent.rhs.name != iterable.rhs.name:
                        # direct access to a data member other than the one being iterated
                        # - fine under the assumption that data members don't overlap (so long as no C style unions in safe code)
                    return True
                return False

            def node_may_alias_iterable(n):
                # we assume that e.g. a function call can't modify the iterable through a global variable / static local
                if not isinstance(n, Identifier):
                    return False
                if iter_var.name == n.name:
                    # TODO allow more uses of the iter var (as well as non-fundamental iter var types) in combination w/ range_for
                    # but only
                    # 1) vec.append/push_back(x) with vec = [] a local
                    # 2) map[x] = x etc (map with local var defn)
                    # 3) x.foo() if an interprocedural analysis proves no use of "mut" in all possible foo methods callable on x
                    #   - current state of propagate_const (copyable) means one can make a mut copy and mutate (so just because x is const 
                    #      (doesn't mean there isn't a non-const access of the iterable as a result of a const method call - though it will be
                    #       marked with a mut annotation)
                    # 4) same for foo(x)
                    return False  
                if n.name in ("this", "self") and not is_over_local_not_aliasing_self:
                    if is_over_self and is_acceptable_use_of_self_this(n):
                        return False
                    return True
                if is_over_self:
                    may_alias_self = False
                    for defn in for_scope.find_defs(n):
                        if isinstance(defn, ParameterDefinition):
                            return True
                        if isinstance(defn, LocalVariableDefinition) and isinstance(defn.defining_node, Call) and defn.defining_node.func.name == "for":
                            iter = defn.defining_node.args[0].rhs
                            if isinstance(iter, AttributeAccess) and iter.lhs.name == "self" and is_acceptable_use_of_self_this(iter.lhs):
                                continue  # this one's ok
                        if any(find_all(defn.defining_node, lambda n: n.name in ["self", "this"] and not is_acceptable_use_of_self_this(n))):
                            may_alias_self = True
                            break
                        if isinstance(defn, LocalVariableDefinition) and any(find_all(defn.defining_node, lambda n: node_may_alias_iterable(n))):
                            may_alias_self = True
                            break
                    return may_alias_self

                if is_over_local_not_aliasing_self:
                    for var_def in for_scope.find_defs(n):
                        if isinstance(var_def, VariableDefinition):
                            parent_block = var_def.defined_node.parent
                            while True:
                                if isinstance(parent_block, Module):
                                    break
                                parent_block = parent_block.parent

                            for local_var in aliased_locals:
                                defined_before = comes_before(parent_block, var_def.defined_node, local_var)
                                if defined_before:
                                    return True
                    return False

                if isinstance(var_def := for_scope.find_def(n), VariableDefinition):
                    # TODO allow more cases where the defined node doesn't alias the iterable?
                    return True

                return False

            if not any(find_all(for_body, node_may_alias_iterable)):

                return node

        elif isinstance(iterable, Identifier):
            # marked as ref elsewhere
            return node

        #iterable = _ban_references_lambda(iterable)
        #if iterable:
        #    node.args = [iter_var, iterable]
        return node

    new_args = []
    found_new = False
    for a in node.args:
        new = safety_checks(a)
        if new:
            new_args.append(new)
            found_new = True
        else:
            new_args.append(a)

    if found_new:
        node.args = new_args

    if node.func:
        new = safety_checks(node.func)
        if new:
            node.func = new

    if 0 and isinstance(node, Call) and not is_def_or_class_like(node) and not node.func.name in ["decltype", "static_assert", "if", "while", "for", "include", "defined", "namespace"] and not (isinstance(node.parent, Call) and is_def_or_class_like(node.parent)):
        # handled in codegen (needs to ignore class constructor calls (e.g. implicit make_shared)
        ban_derefable = Call(Identifier("CETO_BAN_RAW_DEREFERENCABLE"), [node])
        ban_derefable.parent = node.parent
        node.parent = ban_derefable
        ban_derefable.scope = node.scope
        return ban_derefable

    if isinstance(node, Call) and node.func.name == "unsafe" and len(node.args) != 0:
        if isinstance(node.parent, Module):
            raise SemanticAnalysisError("TODO unsafe blocks at Module scope - use an unsafe() call at the top of file for now", node)
        if len(node.args) != 1:
            raise SemanticAnalysisError("unsafe takes 1 arg - an expression or a Block", node)
        if isinstance(node.args[0], Block):
            block_args = node.args[0].args
        else:
            block_args = [node.args[0]]

        # use the existing behaviour of if-expressions for unsafe blocks
        # but with an "unsafe()" call at the beginning that automatically marks the rest of the block as unsafe
        # (we want to avoid the scoping machinery / leave unsafe scopes to codegen for now)
        block_args = [Call(Identifier("unsafe"), [])] + block_args
        unsafe_if = Call(Identifier("if"), [IntegerLiteral("1", None), Block(block_args)])
        return unsafe_if

    return node


def no_references_in_subexpressions_old(node):

    from ceto.compiler import cmdargs
    if not cmdargs._norefs:
        return node

    if isinstance(node, Template) and node.func.name == "include":
        return None

    if isinstance(node, BinOp) and node.op == "in" and node.parent.func and node.parent.func.name == "for" and len(node.parent.args) == 2 and isinstance(node.parent.args[1], Block):
        iterable = node.rhs
        iter_var = node.lhs
        for_body = node.parent.args[1]

        if isinstance(iterable, Identifier) and any(find_all(for_body, lambda n: n.name == iterable.name)):
            raise SemanticAnalysisError("you may not refer to the iterable in the body of a for loop!", iterable)
        elif isinstance(iterable, AttributeAccess) and isinstance(iterable.lhs, Identifier):

            for_scope = node.parent.scope

            is_over_self = iterable.lhs.name == "self"
            is_over_local_not_aliasing_self = False
            if 0 and not is_over_self:
                is_over_local_not_aliasing_self = True

                for defn in for_scope.find_defs(iterable.lhs):
                    if isinstance(defn, ParameterDefinition):
                        is_over_local_not_aliasing_self = False
                        break
                    elif isinstance(defn, LocalVariableDefinition): # and rhs of defining assignment doesn't alias self
                        pass

            def node_may_alias_iterable(n):
                # we assume that e.g. a function call can't modify the iterable through a global variable / static local
                if not isinstance(n, Identifier):
                    return False
                if iter_var.name == n.name:
                    return False
                if n.name in ("this", "self") and not is_over_local_not_aliasing_self:
                    return True
                assert 0
                if is_over_self:
                    may_alias_self = False
                    for defn in for_scope.find_defs(n):
                        if any(find_all(defn.defining_node, lambda n: n.name in ["self", "this"])):
                            may_alias_self = True
                            break
                    assert 0
                    return may_alias_self
                if isinstance(var_def := for_scope.find_def(n), VariableDefinition):
                    #if var_def.defined_node.scope == 
                    # TODO allow more cases where the defined node doesn't alias the iterable

                    return True
                return False

            if not any(find_all(for_body, node_may_alias_iterable)):
                # no need to ban iterating over this maybe reference
                return node

        iterable = no_references_in_subexpressions(iterable)
        if iterable:
            node.args = [iter_var, iterable]
        return node

    if isinstance(node, BinOp) and isinstance(node.parent, Block) and node.op in ["+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "~=", ">>=", "<<="]:
        rhs = no_references_in_subexpressions(node.rhs)
        if rhs:
            node.args = [node.lhs, rhs]
        return node

    new_args = []
    found_new = False
    for a in node.args:
        new = no_references_in_subexpressions(a)
        if new:
            new_args.append(new)
            found_new = True
        else:
            new_args.append(a)

    if found_new:
        node.args = new_args

    if node.func:
        new = no_references_in_subexpressions(node.func)
        if new:
            node.func = new

    if isinstance(node, Module):
        return node

    # Note we should do a better job banning Assign in subexpressions even though the Assign vs NamedParameter
    # distinction was meant to tackle this in the simple case of x=y in a Call
    if isinstance(node, (Block, TypeOp, ListLiteral, BracedLiteral, ScopeResolution, Template, Identifier, Assign, NamedParameter, IntegerLiteral, FloatLiteral, StringLiteral)):
        return None

    if isinstance(node.parent, (Block, TypeOp)):
        return None

    if isinstance(node.parent, (Call, BracedCall, Template, ArrayAccess)) and node is node.parent.func:
        return None

    if isinstance(node.parent, Call) and node.parent.func.name in ["if", "while"]:
        return None

    if isinstance(node.parent, Call) and is_def_or_class_like(node.parent):
        return None

    if isinstance(node, Call) and is_call_lambda(node):
        return None

    if isinstance(node, Call):
        pass

    if isinstance(node.parent, Call) and node.parent.func.name == "for":
        return None

    if isinstance(node.parent, ArrayAccess) and node.parent.func.name == "lambda":
        return None

    if isinstance(node, AttributeAccess):
        attr_lhs = node.lhs
        
        # TODO arguably we should allow this->foo to be a reference regardless of the safety of ->
        # This this-> is arguably ok too (*this is unsafe at least due to current object slicing capabilities)

        if attr_lhs.name == "self":
            # Access to one's own datamembers is always fine in a method 
            # (any invalid use in a for loop will trigger a static_assert on the for loop 
            #   iter rather thatn the self use in the for loop body)
            return node

        while isinstance(attr_lhs, (AttributeAccess, ScopeResolution)):
            attr_lhs = attr_lhs.lhs

        if isinstance(attr_lhs, Identifier) and attr_lhs.name != "self" and not attr_lhs.scope.find_def(attr_lhs):
            # implicit scope resolution
            return None

    # note that banning e.g. dereferenable (requires { *foo } ) types on the lhs of an assignment should use
    # the "no implicit conversions in assignments" logic in codegen_assign

    if isinstance(node.parent, Assign):
        # a C++ reference is ok as the type of the lhs of an assignment because C++ will perform a copy without 
        # an explicit reference type (which, for a local variable, will TODO require an unsafe annotation even if const)
        return None

#    code = """(lambda[ref] (:
#    static_assert(not std::is_reference_v<decltype(ceto_private_placeholder)>)
#    return ceto_private_placeholder
#):decltype(auto))()"""

#    from .parser import parse
#    ban_references_lambda = parse(code).args[0]
#    print(ban_references_lambda.ast_repr(ceto_evalable=False, preserve_source_loc=False))
#    import sys
#    sys.exit(-1)

    clone = node.clone()

    ban_references_lambda = Call(TypeOp(":", [Call(ArrayAccess(Identifier("lambda", ), [Identifier("ref", ), ], ), [Block([Call(Identifier("static_assert", ), [UnOp("not", [ScopeResolution("::", [Identifier("std", ), Template(Identifier("is_reference_v", ), [Call(Identifier("overparenthesized_decltype", ), [clone, ], ), ], ), ], )], ), ], ), SyntaxTypeOp(":", [Identifier("return"), node], ), ], ), ], ), Call(Identifier("decltype", ), [Identifier("auto", ), ], ), ], ), [], )

    #ban_references_lambda = Call(Identifier("CETO_BAN_REFS"), [node])

    ban_references_lambda.parent = node.parent
    node.parent = ban_references_lambda
    clone.parent = ban_references_lambda
    clone.scope = node.scope
    ban_references_lambda.scope = node.scope
    #ban_references_lambda = basic_semantic_analysis(ban_references_lambda)

    return ban_references_lambda


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


def _same_binop_inorder_traversal(binop: Node, binop_class, func):
    assert issubclass(binop_class, BinOp)

    if isinstance(binop, binop_class):
        if not _same_binop_inorder_traversal(binop.lhs, binop_class, func):
            return False
        if not _same_binop_inorder_traversal(binop.rhs, binop_class, func):
            return False
        return True
    else:
        return func(binop)

def same_binop_inorder_traversal(binop: Node, func):
    return _same_binop_inorder_traversal(binop, binop.__class__, func)


def nested_same_binop_to_list(binop: Node):
    elements = []

    if binop is None:
        return elements

    def callback(e):
        elements.append(e)
        return True

    same_binop_inorder_traversal(binop, callback)

    return elements


def list_to_typed_node(lst):
    op = None
    first = None
    if not lst:
        return None
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

    # TODO this can perhaps be removed (build_parents call before/after macro expansion is new - we're undoing it here so that latter existing stages are unaffected)
    node.parent = None

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

        if isinstance(op, Call) and op.func.name == "defmacro":
            # we don't want to validate anything in a defmacro body 
            return Call(Identifier("ceto_private_elided_defmacro"), [])

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
            elif op.func.name == "requires":
                if len(op.args) == 0:
                    raise SemanticAnalysisError("empty requires expression", op)
                if not isinstance(op.args[-1], Block):
                    # last arg becomes one-element block
                    op = Call(op.func, op.args[0:-1] + [Block([op.args[-1]])], op.source)
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


def warn_and_remove_redundant_parenthesese(expr, error=False):

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
    if call.func.name in ["def", "defmacro", "lambda", "class", "struct"]:
        return True
    if isinstance(call.func, ArrayAccess) and call.func.func.name == "lambda":
        # lambda with explicit capture list
        return True
    return False


# TODO Writing this with the exterior visitation was a bad idea - prevents things
# like easily ignoring Template args (without accessing .parent) when determining if a variable
# type is a declaration. Should be moved to C++ but arg flattening needs to be addressed first.
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
                if index > 0 and (thenscope := call.args[index - 1].scope):
                    a.scope = thenscope.enter_scope()
                else:
                    a.scope = call.scope.enter_scope()
            elif call.func.name in ["if", "for", "while"]:
                a.scope = call.scope.enter_scope()
            elif is_def_or_class_like(call):
                a.scope = call_inner_scope

                if call.func.name in ["class", "struct"]:
                    #call.scope.add_class_definition(
                    pass  # TODO
                elif call.func.name == "def":
                    def_name = call.args[0]
                    while isinstance(def_name, (Template, Call)):
                        def_name = def_name.func
                    call.scope.add_function_definition(FunctionDefinition(call, def_name))

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
            elif isinstance(a, Block) and is_def_or_class_like(call):
                if call.func.name in ["class", "struct"]:
                    a.scope.in_function_body = False
                    a.scope.in_class_body = True
                else:
                    #a.scope.in_class_body = False  # maybe we should do this
                    a.scope.in_function_body = True

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


class ImplicitLambdaCaptureVisitor:

    def visit_Call(self, call):
        # TODO needs fixes + fixes for explicit capture lists in _decltype_str
        return call

        def replace_lambda(old_call, new_capture_list):
            # this is why scope/parent/declared_type are unavailable to the macro system!
            # TODO allow scope lookup in the macro system and selfhost passes without this brittleness
            lmb = Identifier("lambda")
            lmb.scope = old_call.func.scope
            new_call = Call(func=ArrayAccess(func=lmb, args=[]), args=old_call.args)
            new_call.parent = old_call.parent
            new_call.scope = old_call.scope
            if old_call.declared_type:
                new_call.declared_type = old_call.declared_type
                print("new_call.declared_type", new_call.declared_type)
                new_call.declared_type.parent = new_call
                if old_call.declared_type.scope:
                    new_call.declared_type.scope = old_call.declared_type.scope
            new_call.func.parent = new_call
            new_call.func.scope = old_call.func.scope
            block = new_call.args[-1]
            assert isinstance(block, Block)
            last_statement = block.args[-1]
            if hasattr(last_statement, "synthetic_lambda_return_lambda") and last_statement.synthetic_lambda_return_lambda:
                last_statement.synthetic_lambda_return_lambda = new_call
            for a in new_call.args:
                a.parent = new_call
            return new_call

        from .parser import parse

        if not call.func.name == "lambda":
            # we don't want is_call_lambda here (lambdas with explicit capture lists handled in codegen)
            return call

        if not call.parent.scope.in_function_body:
            return replace_lambda(call, [])

        def is_capture(n):
            if not isinstance(n, Identifier):
                return False
            elif isinstance(n.parent, (Call, ArrayAccess, BracedCall, Template)) and n is n.parent.func:
                return False
            elif isinstance(n.parent, AttributeAccess) and n is n.parent.rhs:
                return False
            return True

        # find all identifiers but not call funcs etc or anything in a nested class
        idents = find_all(call, test=is_capture, stop=lambda c: isinstance(c.func, Identifier) and c.func.name in ["class", "struct"])

        idents = {i.name: i for i in idents}.values()  # remove duplicates

        possible_captures = []
        for i in idents:
            if i.name == "self":
                possible_captures.append(i.name)
            elif isinstance(i.parent, Call) and i.parent.func.name in ["def", "lambda"]:
                pass  # don't capture a lambda parameter
            elif (d := i.scope.find_def(i)) and isinstance(d, (LocalVariableDefinition, ParameterDefinition)):
                defnode = d.defined_node
                is_capture = True
                while defnode is not None:
                    if defnode is call:
                        # defined in lambda or by lambda params (not a capture)
                        is_capture = False
                        break
                    defnode = defnode.parent
                if is_capture:
                    possible_captures.append(i.name)

        if isinstance(call.parent, Call) and call is call.parent.func:
            # immediately invoked (TODO: nonescaping)
            # capture by const ref: https://stackoverflow.com/questions/3772867/lambda-capture-as-const-reference/32440415#32440415
            capture_list = ["&" + i + " = " + "std::as_const(" + i + ")" for i in possible_captures]
        else:
            # capture only a few things by const value (shared/weak instances, arithithmetic_v, enums):
            capture_list = [i + " = " + "ceto::default_capture(" + i + ")" for i in possible_captures]

        # this is lazy but it's fine
        capture_list_ast = [parse(s).args[0] for s in capture_list]

        new_lambda = replace_lambda(call, capture_list_ast)
        #for capture_list_arg in new_lambda.func.args:
        # TODO need to add_variable_definition for newly added capture list
        #    capture_list_arg.scope
        return new_lambda


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


counter = 0

def gensym(prefix=None):
    global counter
    counter += 1
    pre = "ceto__private__"
    if prefix is not None:
        pre += prefix
    return pre + str(counter)


def unquote_remover(node):
    def _replace(unquote):
        if isinstance(unquote, Call) and unquote.func.name == "unquote":
            if len(unquote.args) != 1:
                raise SemanticAnalysisError("unquote takes a single arg", unquote)
            return Identifier(gensym())
        return None

    replacements = {}
    new_args = []

    for arg in node.args:
        if stand_in := _replace(arg):
            replacements[stand_in] = arg.args[0]
            new_args.append(stand_in)
        else:
            subreplacements, arg = unquote_remover(arg)
            replacements.update(subreplacements)
            new_args.append(arg)

    node.args = new_args

    if stand_in := _replace(node.func):
        replacements[stand_in] = node.func.args[0]
        node.func = stand_in
    elif node.func:
        subreplacements, node.func = unquote_remover(node.func)
        replacements.update(subreplacements)

    return replacements, node


def replace_node(node: Node, replacing_function):
    node.args = [replace_node(replacing_function(a), replacing_function) for a in node.args]
    if node.func:
        node.func = replace_node(replacing_function(node.func), replacing_function)
    return node


def quote_expander(node):
    from .parser import parse

    def _expand(quote):
        if isinstance(quote, Call) and quote.func.name == "quote":
            if len(quote.args) != 1:
                raise SemanticAnalysisError("quote takes a single arg", quote)
            replacements, quote_arg = unquote_remover(quote.args[0])
            repr = quote_arg.ast_repr(preserve_source_loc=False, ceto_evalable=True)
            for r in replacements:
                repr = repr.replace(r.ast_repr(preserve_source_loc=False, ceto_evalable=True), r.name)
            expanded = parse(repr).args[0]

            for r in replacements:
                expanded = replace_node(expanded, lambda n: quote_expander(replacements[r]) if n.name == r.name else n)

            return expanded
        return None

    new_args = []

    for arg in node.args:
        if expanded := _expand(arg):
            new_args.append(expanded)
        else:
            arg = quote_expander(arg)
            new_args.append(arg)

    node.args = new_args

    if expanded := _expand(node.func):
        node.func = expanded
    elif node.func:
        node.func = quote_expander(node.func)

    return node


def create_macro_impl_module(node: Node, macro_definition: MacroDefinition, macro_impl: TypeOp):
    """create a module with the defmacro of `macro_definition` replaced by the `macro_impl` implementing the body of the macro"""

    new_args = [macro_impl if a is macro_definition.defmacro_node
                           else create_macro_impl_module(a, macro_definition, macro_impl)
                for a in node.args]
    if isinstance(node, Module):
        # allow constant evaluation of any other code in module (or included by
        # module) except "main" (even though not strictly necessary to remove from dll)
        new_args = [a for a in new_args if not (isinstance(a, Call) and a.func.name == "def" and a.args[0].name == "main")]
        return Module(new_args)
    elif isinstance(node, Block):
        return Block(new_args)
    return node


def prepare_macro_ready_callback(module):

    macro_number = 0

    def on_macro_def(mcd: MacroDefinition, replacements):
        from .parser import parse
        from .codegen import codegen

        nonlocal macro_number

        mcd.impl_function_name = f"macro_impl{macro_number}"

        if mcd.defmacro_node.source.header_file_cth:
            module_path = mcd.defmacro_node.source.header_file_cth
        else:
            from .compiler import cmdargs
            module_path = cmdargs.filename

        module_name = os.path.basename(module_path)
        module_dir = os.path.dirname(module_path)

        impl_path = os.path.join(module_dir, f"{module_name}.macro_impl.{macro_number}")

        dll_path = impl_path
        if sys.platform == "win32":
            dll_path += ".dll"
        elif sys.platform == "darwin":
            dll_path += ".dylib"
        else:
            dll_path += ".so"

        mcd.dll_path = dll_path

        macro_number += 1

        if os.path.isfile(dll_path):
            # TODO this doesn't handle changes in dependent headers
            # - To fix we should be checking the mtime of the header path of all preceding
            #   nodes in the module. Note comment in parser.py about not setting header path 
            #   on nodes from a subinclude (easier caching??) - may interfere with fix
            module_time = os.path.getmtime(module_path)
            dll_time = os.path.getmtime(dll_path)
            if dll_time >= module_time:
                return
            elif "ceto_private" in module_name:
                # hack to avoid unnecessary recompilation of standard library macros: module_path mtime updated after dll mtime (due to pip install moving files after macro compilation)
                return

        # apply current replacement decisions at the time of encountering the current macro def (for a defmacro that relies on other defmacros)
        # allowing expand_macros to do the replacements in place (add mutable visitor) would avoid this
        defmacro_node = replace_macro_expansion(mcd.defmacro_node, replacements)
        new_module = replace_macro_expansion(module, replacements)
        #mcd.pattern = replace_macro_expansion(mcd.pattern, replacements)  # not necessary? or is it too late to even handle this (bug)
        parameters = { k: replace_macro_expansion(v, replacements) for k, v in mcd.parameters.items() }  # not necessary?

        print("mcd", defmacro_node)

        # prepare a function that implements the body of the "defmacro"
        impl_str = f'def ({mcd.impl_function_name}: extern:"C":CETO_EXPORT:noinline, CETO_PRIVATE_params: const:std.map<std.string, Node>:ref:\n'
        indt = "    "
        for param_name in parameters:
            init_param = 'CETO_PRIVATE_params.at("' + param_name + '")'
            for param in defmacro_node.args[1:]:
                if isinstance(param, TypeOp) and param_name == param.lhs.name:
                    if isinstance(param.rhs, Identifier):
                        init_param = "asinstance(" + init_param + ", " + param.rhs.name + ")"
                    elif isinstance(param.rhs, ListLiteral):
                        init_param = init_param + ".args"
                    elif isinstance(param.rhs, BitwiseOrOp):
                        non_none = [b.name for b in param.rhs.args if isinstance(b, Identifier) and b.name != "None"]
                        if len(non_none) == 1:
                            alternate_type = non_none[0]
                        else:
                            alternate_type = "Node"
                        init_param = "if (CETO_PRIVATE_params.find('" + param_name + "') != CETO_PRIVATE_params.end():\n" + indt * 2 + "asinstance(CETO_PRIVATE_params.at('" + param_name + "'), " + alternate_type + ")\n" + indt + "else:\n" + indt * 2 + "CETO_PRIVATE_none: " + alternate_type  + " = None; CETO_PRIVATE_none\n" + indt + ")\n"
                    break

            impl_str += indt + param_name + " = " + init_param + "\n"
        impl_str += indt + "pass\n): std.variant<Node, ceto.macros.Skip>"

        macro_impl = parse(impl_str).args[0]
        assert isinstance(macro_impl, TypeOp)
        impl_def = macro_impl.args[0]
        assert isinstance(impl_def, Call)
        impl_block = impl_def.args[-1]
        assert isinstance(impl_block, Block)
        defmacro_body = defmacro_node.args[-1]
        assert isinstance(defmacro_body, Block)

        expanded = quote_expander(defmacro_body)
        impl_block.args = impl_block.args[:-1] + expanded.args

        macro_impl_module = create_macro_impl_module(new_module, mcd, macro_impl)

        impl_index = next(i for i, v in enumerate(macro_impl_module.args) if v.args and v.args[0].args and v.args[0].args[0].args and v.args[0].args[0].args[0].name == mcd.impl_function_name)
        macro_impl_module_args = macro_impl_module.args[0:impl_index + 1]
        macro_impl_module.args = macro_impl_module_args

        package_dir = os.path.dirname(__file__)
        selfhost_dir = os.path.join(package_dir, os.pardir, "selfhost")
        toremove = []

        # prepare dependency of macro dll on a few selfhost sources
        for orig_name in ["ast.cth", "utility.cth", "range_utility.cth", "visitor.cth"]:
            destination_name = "ceto__private__" + orig_name
            destination_path = os.path.join(module_dir, destination_name)
            if os.path.isfile(destination_path):
                continue
            for d in [package_dir, selfhost_dir]:
                orig_path = os.path.join(d, orig_name)
                if os.path.isfile(orig_path):
                    if orig_name == "ast.cth":
                        with open(orig_path) as f:
                            ast_str = f.read()
                        ast_str = ast_str.replace("include (utility)", "include (ceto__private__utility)")
                        ast_str = ast_str.replace("include (range_utility)", "include (ceto__private__range_utility)")
                        ast_str = ast_str.replace("include (visitor)", "include (ceto__private__visitor)")
                        with open(destination_path, "w") as f:
                            f.write(ast_str)
                    else:
                        shutil.copyfile(orig_path, destination_path)
                    toremove.append(destination_path)
                    break

        include_ast = parse("include (ceto__private__ast)")

        for f in toremove:
            os.remove(f)

        macro_impl_module.args = include_ast.args + macro_impl_module.args

        # Ignore any other defmacro nodes (we don't want to compile them just yet - we're busy with the current defmacro.
        # (TODO is this necessary now that we're discarding all nodes in module after the current macro impl?)
        #macro_impl_module.args = [a for a in macro_impl_module.args if not (isinstance(a, Call) and a.func.name == "defmacro")]

        # However, we do want to run macro expansion on the body of our current defmacro:
        macro_impl_module = macro_expansion(macro_impl_module)

        macro_impl_module = semantic_analysis(macro_impl_module)
        macro_impl_code = codegen(macro_impl_module)

        dll_cpp = impl_path + ".cpp"

        with open(dll_cpp, "w") as f:
            f.write(macro_impl_code)

        project_dir = os.path.join(os.path.dirname(__file__), os.pardir)

        include_opts = f"-I{os.path.join(project_dir, 'include')} -I{os.path.join(project_dir, 'include', 'kit_local_shared_ptr')} -I{os.path.join(project_dir, 'selfhost')} -I{os.path.dirname(__file__)} -I{os.path.join(os.path.dirname(__file__), 'kit_local_shared_ptr')}"

        if sys.platform == "win32":
            include_opts = include_opts.replace('-I', '/I')
            build_command = f"cl.exe /std:c++20 /Wall /permissive- /EHsc {include_opts} /LD /Fe:{dll_path} {dll_cpp}"
        else:
            dll_options = f"-fPIC -shared -Wl,-soname,{dll_path}.so -ldl"
            if sys.platform == "darwin":
                dll_options = "-dynamiclib"
            build_command = f"c++ -Wall -Wextra -std=c++20 -O2 {include_opts} {dll_options} -o {dll_path} {dll_cpp}"

        print(build_command)
        try:
            output = subprocess.check_output(build_command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            print(e)
            raise

    return on_macro_def


def replace_macro_expansion(node: Node, replacements):
    if node in replacements:
        return replacements[node].clone()

    node.args = [replace_macro_expansion(a, replacements) for a in node.args]
    if node.func:
        node.func = replace_macro_expansion(node.func, replacements)

    return node


def macro_expansion(expr: Module):
    assert isinstance(expr, Module)

    expr = build_parents(expr)

    while True:
        replacements = expand_macros(expr, prepare_macro_ready_callback(expr))
        print("macro replacements", replacements)
        if not replacements:
            break
        expr = replace_macro_expansion(expr, replacements)
        expr = build_parents(expr)

    return expr


def basic_semantic_analysis(expr: Module) -> Module:
    expr = build_types(expr)
    expr = build_parents(expr)
    expr = apply_replacers(expr, [ScopeVisitor()])
    expr = apply_replacers(expr, [ImplicitLambdaCaptureVisitor()])
    return expr


def semantic_analysis(expr: Module) -> Module:
    assert isinstance(expr, Module) # enforced by parser

    expr = one_liner_expander(expr)
    expr = assign_to_named_parameter(expr)
    expr = warn_and_remove_redundant_parenthesese(expr)

    expr = basic_semantic_analysis(expr)
    expr = safety_checks(expr)

    def clearscope(n):
        n.scope = None
        return n

    expr = replace_node(expr, clearscope)

    expr = basic_semantic_analysis(expr)

    def debug_defs(node):
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
        print("class_def", node.scope.lookup_class(node))
        print("function_def", node.scope.lookup_function(node))
        for a in node.args:
            debug_defs(a)
            debug_defs(a.func)

    # debug_defs(expr)

    return expr
