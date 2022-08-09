import ast

__all__ = ("delegate", "delegates")


_get_name = "_get_{0}"
_set_name = "_set_{0}"
_del_name = "_del_{0}"


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


def _chop_and_collect(obj, attr):
    return ["self"] + obj.split(".") + attr.split(".")


def make_getter(obj, attr):
    chunks = _chop_and_collect(obj, attr)
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


def make_setter(obj, attr):
    chunks = _chop_and_collect(obj, attr)
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


def make_deleter(obj, attr):
    chunks = _chop_and_collect(obj, attr)
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


def make_accessor_module(obj, attr):
    return ast.Module(
        body=[
            make_getter(obj, attr),
            make_setter(obj, attr),
            make_deleter(obj, attr),
        ],
        type_ignores=[],
    )


def _as_list_or_tuple(arg):
    if not isinstance(arg, (list, tuple)):
        arg = [arg]
    return arg


def delegate(to, attrs=None, names=None, /):
    attrs = _as_list_or_tuple(attrs)
    if names is None:
        names = [attr.split(".")[-1] for attr in attrs]
    names = _as_list_or_tuple(names)

    def wrapper(cls):
        ns = {}
        for attr, name in zip(attrs, names):
            tree = make_accessor_module(to, attr)
            exec(compile(tree, "<ast>", "exec"), ns)

            attr_name = attr.split(".")[-1]
            fget = ns[_get_name.format(attr_name)]
            fset = ns[_set_name.format(attr_name)]
            fdel = ns[_del_name.format(attr_name)]
            setattr(cls, name, property(fget, fset, fdel))

        return cls
    return wrapper


def delegates(*args):
    def wrapper(cls):
        for arg in args:
            cls = delegate(*arg)(cls)

        return cls
    return wrapper


def _main():
    from dataclasses import dataclass

    @dataclass
    class Fridge:
        brand: str

        def cool(self):
            return "-18° C"

    @dataclass
    class Oven:
        brand: str

        def heat(self):
            return "200° C"

    @dataclass
    class Kitchen:
        fridge: Fridge
        oven: Oven

        def bake(self):
            return "Cake"

    @delegate("kitchen", "bake")
    @delegate("kitchen", ["oven", "fridge"])
    @delegate("kitchen", "bake", "make_cake")
    @dataclass
    @delegates(
        ("kitchen.fridge", "cool"),
        ("kitchen", "oven.heat"),
    )
    class House:
        kitchen: Kitchen

    fridge = Fridge("Bosch")
    oven = Oven("Electrolux")
    kitchen = Kitchen(fridge, oven)
    house = House(kitchen)

    print(house.oven, house.fridge)
    print(house.bake())
    print(house.cool())
    print(house.heat())
    print(house.make_cake())


if __name__ == "__main__":
    _main()
