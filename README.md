# composition-delegation

>**Composition** is one of the fundamental concepts of Object-Oriented Programming. 
In this concept, we will describe a class that references to one or more objects of other classes as an Instance variable. 
Here, by using the class name or by creating the object we can access the members of one class inside another class. 
It enables creating complex types by combining objects of different classes. 
It means that a class **Composite** can contain an object of another class **Component**.
(source: www.geeksforgeeks.org/inheritance-and-composition-in-python)

Because this sounds very abstract, let's assume we have a house that consists of several rooms (e.g. a kitchen) that contain devices such as a fridge and an oven. 
We could implement this as shown below:

```python
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

@dataclass
class House:
    kitchen: Kitchen
```

When we create a house (see below), we can access its oven as `house.kitchen.oven` or we can bake by typing `house.kitchen.bake()`.

```python
fridge = Fridge("Bosch")
oven = Oven("Electrolux")
kitchen = Kitchen(fridge, oven)
house = House(kitchen)
```

We can use the decorator `@delegate` to delegate the call `bake()` to the kitchen.
Baking a cake then becomes as concise as `house.bake()`.

```python
from delegate import delegate

@delegate("kitchen", "bake")
@dataclass
class House:
    ...
```

We can delegate multiple attributes by gathering them into a list. Note that the order of the decorators does not matter. The `delegate` decorator should not interfere with most other decorators.

```python
@dataclass
@delegate("kitchen", ["oven", "fridge"])
class House:
    ...
```

If we want to bake a cake more explicitly , we can do so by specifying a third argument. In the example below, "house.kitchen.make_cake()" is equivalent to "kitchen.bake()".

```python
@delegate("kitchen", "bake", "make_cake")
@dataclass
class House:
    ...
```

Instead of stacking multiple `@delegates` we can use the `@delegates` decorator.
Note also that we delegate deeper attributes as well. Here it doesn`t matter if we use dot indexing on the delegee or attribute side (we can even use it on both sides):

```python
from delegate import delegates

@delegates(
    ("kitchen.fridge", "cool"),
    ("kitchen", "oven.heat"),
)
@dataclass
class House:
    ...
```

Let's now put it all together and let's check if it outputs what we expect:

```python

@delegates(
    ("kitchen", ["oven", "fridge", "bake"]),
    ("kitchen", "bake", "make_cake"),
    ("kitchen.fridge", "cool"),
    ("kitchen.oven", "heat"),
)
@dataclass
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

'Oven(brand="Electrolux") Fridge(brand="Bosch")'
'Cake'
'-18° C'
'200° C'
'Cake'
```

The delegation is happens via the built-in `property`. Therefore, it is also possible to set and delete the delegated attribute. 
In addition, accessing the attribute in this way is a lot faster compared to an implementation with descriptors.