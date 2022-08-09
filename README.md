# composition-delegation

```python
from dataclasses import dataclass, field
from delegate import delegate, delegates

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

'Oven(brand="Electrolux") Fridge(brand="Bosch")'
'Cake'
'-18° C'
'200° C'
'Cake'
```

