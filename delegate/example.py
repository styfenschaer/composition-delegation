from dataclasses import dataclass

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


@delegates(
    ("kitchen", ["oven", "fridge", "bake"]),
    ("kitchen", "bake", "make_cake"),
    ("kitchen.fridge", "cool"),
    ("kitchen.oven", "heat"),
)
@dataclass
class House:
    kitchen: Kitchen


def main():
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
    main()
