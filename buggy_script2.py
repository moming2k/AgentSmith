import math
import os


def calculate_area(radius):
    area = 3.14 * radius * radius
    return area


def add_numbers(a, b):
    result = a + b
    return result


class Calculator:
    def __init__(self):
        self.number1 = 10
        self.number2 = 20

    def perform_calculations(self):
        self.sum = add_numbers(self.number1, self.number2)
        self.area = calculate_area(self.number1)

    def display_results(self):
        print("Sum:", self.sum)
        print("Area:", self.area)


calc = Calculator()
calc.perform_calculations()
calc.display_results()
