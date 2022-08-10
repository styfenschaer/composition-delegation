import ast

__all__ = ("delegate", "delegates")


_get_name = "fget_{0}"
_set_name = "fset_{0}"
_del_name = "fdel_{0}"


def deep_attribute(chunks, ctx):
    attr = ast.Attribute(
        value=ast.Name(
            id=chunks.pop(0),
            ctx=ast.Load(),
        ),
        attr=chunks.pop(0),
        ctx=ast.Load(),
    )
    while chunks:
        attr = ast.Attribute(
            value=attr,
            attr=chunks.pop(0),
            ctx=ast.Load(),
        )
    attr.ctx = ctx
    return attr


def _chop_and_collect(owner, attr):
    return ["self"] + owner.split(".") + attr.split(".")


def make_getter(owner, attr):
    chunks = _chop_and_collect(owner, attr)
    name = chunks[-1]

    tree = ast.FunctionDef(
        name=_get_name.format(name),
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(
                    arg="self",
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[
            ast.Return(
                value=deep_attribute(chunks, ctx=ast.Load()),
            ),
        ],
        decorator_list=[],
    )
    return ast.fix_missing_locations(tree)


def make_setter(owner, attr):
    chunks = _chop_and_collect(owner, attr)
    name = chunks[-1]

    tree = ast.FunctionDef(
        name=_set_name.format(name),
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(
                    arg="self",
                ),
                ast.arg(
                    arg="val",
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[
            ast.Assign(
                targets=[
                    deep_attribute(chunks, ctx=ast.Store()),
                ],
                value=ast.Name(
                    id="val",
                    ctx=ast.Load(),
                ),
            ),
        ],
        decorator_list=[],
    )
    return ast.fix_missing_locations(tree)


def make_deleter(owner, attr):
    chunks = _chop_and_collect(owner, attr)
    name = chunks[-1]

    tree = ast.FunctionDef(
        name=_del_name.format(name),
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(
                    arg="self",
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[
            ast.Delete(
                targets=[
                    deep_attribute(chunks, ctx=ast.Del()),
                ],
            ),
        ],
        decorator_list=[],
    )
    return ast.fix_missing_locations(tree)


def make_accessor_module(owner, attr):
    return ast.Module(
        body=[
            make_getter(owner, attr),
            make_setter(owner, attr),
            make_deleter(owner, attr),
        ],
        type_ignores=[],
    )


def _as_list_or_tuple(arg):
    if not isinstance(arg, (list, tuple)):
        arg = [arg]
    return arg


def delegate(to, what, as_=None, /):
    what = _as_list_or_tuple(what)
    if as_ is None:
        as_ = [w.split(".")[-1] for w in what]
    as_ = _as_list_or_tuple(as_)

    def wrapper(cls):
        ns = {}
        for what_i, as_i in zip(what, as_):
            tree = make_accessor_module(to, what_i)
            exec(compile(tree, "<ast>", "exec"), ns)

            attr_name = what_i.split(".")[-1]
            fget = ns[_get_name.format(attr_name)]
            fset = ns[_set_name.format(attr_name)]
            fdel = ns[_del_name.format(attr_name)]
            setattr(cls, as_i, property(fget, fset, fdel))

        return cls
    return wrapper


def delegates(*args):
    def wrapper(cls):
        for arg in args:
            cls = delegate(*arg)(cls)

        return cls
    return wrapper
