# Datatypes and variables
# int - int, unsigned, count # float - real numbers # char - characters # string - collection of characters
# void - empty # boolean - true or false

import pandas as pd


class FirstClass():

    def __init__(self, value):
        self.test = dict()
        self.listery = list()
        self.dataframer = pd.DataFrame()
        self.value = value

### inheritance
# parent class
class Bird:

    def __init__(self):
        print("Bird is ready")

    def whoisThis(self):
        print("Bird")

    def swim(self):
        print("Swim faster")


# child class
class Penguin(Bird):

    def __init__(self):
        # call super() function
        super().__init__()
        print("Penguin is ready")

    def whoisThis(self):
        print("Penguin")

    def run(self):
        print("Run faster")


peggy = Penguin()
peggy.whoisThis()
peggy.swim()
peggy.run()

##Encapsulation
class Computer:

    def __init__(self):
        self.__maxprice = 900

    def sell(self):
        print("Selling Price: {}".format(self.__maxprice))

    def setMaxPrice(self, price):
        self.__maxprice = price

c = Computer()
c.sell()

# change the price
c.__maxprice = 1000
c.sell()

# using setter function
c.setMaxPrice(1000)
c.sell()



#ploymorphism
class Parrot:

    def fly(self):
        print("Parrot can fly")

    def swim(self):
        print("Parrot can't swim")


class Penguin:

    def fly(self):
        print("Penguin can't fly")

    def swim(self):
        print("Penguin can swim")


# common interface
def flying_test(bird):
    bird.fly()


# instantiate objects
blu = Parrot()
peggy = Penguin()

# passing the object
flying_test(blu)

flying_test(peggy)

class MyClass:
    "this is my second class"
    a = 10
    def func(self):
        print('Hello')

print(MyClass.a)
print(MyClass.func)
print(MyClass.__doc__)

ob = MyClass()
ob.func()

class ComplexNumber:
    def __init__(self, r=0, i=0):
        self.real = r
        self.imag = i
    def getData(self):
        print("{0}+{1}j".format(self.real, self.imag))

c1 = ComplexNumber(2,3)
c1.getData()
c2 = ComplexNumber(5)
c2.attr = 10
print(c2.real, c2.imag, c2.attr)
c1 = ComplexNumber(2,3)
del c1.imag
c1.getData()
del ComplexNumber.getData
c1.getData()

class Polygon:
    def __init__(self, no_of_sides):
        self.n = no_of_sides
        self.sides = [0 for i in range(no_of_sides)]
    def inputSides(self):
        self.sides = [float(input("Enter side " + str(i+1)+":")) for i in range(self.n)]
    def dispSides(self):
        for i in range(self.n):
            print("Side", i+1, "is", self.sides[i])

class Triangle(Polygon):
    def __init__(self):
        super().__init__(3)

    def findArea(self):
        a, b, c = self.sides
        # calculate the semi-perimeter
        s = (a + b + c) / 2
        area = (s*(s-a)*(s-b)*(s-c)) ** 0.5
        print('The area of the triangle is %0.2f' %area)






