# composition-delegation

```python
from dataclasses import dataclass, field
from delegate import delegate

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
    ("kitchen", ["oven", "fridge"]),
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

Oven(brand='Electrolux') Fridge(brand='Bosch')
Cake
-18° C
200° C
```

