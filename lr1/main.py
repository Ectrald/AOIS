from functions import *

print("What do you want to do?")
print("1. converting a number from decimal to binary format")
print("2. subtraction two numbers in an additional code")
print("3. adding two numbers in an additional code")
print("4. multiplication of two numbers in direct code")
print("5. dividing two numbers in direct code")
print("6. add two positive floating point numbers")
a = int(input())

match a:
    case 1:
        num = int(input("Input a number: "))
        print(binary_data(num))
    case 2:
        num1 = int(input("Input a first number: "))
        num2 = int(input("Input a second number: "))
        print(binary_subtraction(num1, num2))
    case 3:
        num1 = int(input("Input a first number: "))
        num2 = int(input("Input a second number: "))
        print(binary_addition(num1, num2))
    case 4:
        num1 = int(input("Input a first number: "))
        num2 = int(input("Input a second number: "))
        print(binary_data(binary_to_signed_decimal(binary_multiplication(num1, num2))))
    case 5:
        num1 = int(input("Input a first number: "))
        num2 = int(input("Input a second number: "))
        division = binary_division(num1, num2)
        print(division)
        print(binary_fixed_point_to_decimal(division))
    case 6:
        num1 = float(input("Input a first number: "))
        num2 = float(input("Input a second number: "))
        print(addition_float(num1, num2))
    case _:
        print("Wrong input")