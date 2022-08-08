import ast
import inspect
import sys


def chop_and_collect(obj, attr):
    return ["self"] + obj.split(".") + attr.split(".")


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


def make_getter(obj, attr):
    chunks = chop_and_collect(obj, attr)
    attr_name = chunks[-1]

    tree = ast.FunctionDef(
        name=attr_name,
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
        decorator_list=[
            ast.Name(
                id="property",
                ctx=ast.Load(),
            ),
        ],
    )
    return ast.fix_missing_locations(tree)


def make_setter(obj, attr):
    chunks = chop_and_collect(obj, attr)
    attr_name = chunks[-1]

    tree = ast.FunctionDef(
        name=attr_name,
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
        decorator_list=[
            ast.Attribute(
                value=ast.Name(
                    id=attr_name,
                    ctx=ast.Load(),
                ),
                attr="setter",
                ctx=ast.Load(),
            ),
        ],
    )
    return ast.fix_missing_locations(tree)


def make_deleter(obj, attr):
    chunks = chop_and_collect(obj, attr)
    attr_name = chunks[-1]

    tree = ast.FunctionDef(
        name=attr_name,
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
        decorator_list=[
            ast.Attribute(
                value=ast.Name(
                    id=attr_name,
                    ctx=ast.Load(),
                ),
                attr="deleter",
                ctx=ast.Load(),
            ),
        ],
    )
    return ast.fix_missing_locations(tree)


def unindented_source(obj):
    lns = inspect.getsourcelines(obj)[0]
    wspaces = len(lns[0]) - len(lns[0].lstrip())
    lns = [ln[wspaces:] for ln in lns]
    return "".join(lns)


def delegate(*args):
    if not isinstance(args[0], (list, tuple)):
        args = args,

    def decorator(cls):
        src = unindented_source(cls)
        tree = ast.parse(src)
        tree.body[0].decorator_list = []

        for to, *objs in args:
            if isinstance(objs[0], (list, tuple)):
                objs = objs[0]

            for obj in objs:
                tree.body[0].body.extend([
                    make_getter(to, obj),
                    make_setter(to, obj),
                    make_deleter(to, obj),
                ])

        tree = ast.fix_missing_locations(tree)

        ns = sys._getframe(1).f_globals
        exec(compile(tree, "<ast>", "exec"), ns)

        return ns.get(cls.__name__)

    return decorator


if __name__ == "__main__":
    from dataclasses import dataclass, field

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
        fridge: field(default_factory=Fridge)
        oven: field(default_factory=Oven)

        def bake(self):
            return "Cake"

    @dataclass
    @delegate(
        ("kitchen", "oven", "fridge"),
        ("kitchen", "bake"),
        ("kitchen.fridge", "cool"),
        ("kitchen", "oven.heat"),
    )
    class House:
        kitchen: field(default_factory=Kitchen)

    fridge = Fridge("Bosch")
    oven = Oven("Electrolux")
    kitchen = Kitchen(fridge, oven)
    house = House(kitchen)

    print(house.oven, house.fridge)
    print(house.bake())
    print(house.cool())
    print(house.heat())
