#!/usr/bin/env python3
# Enhanced calculator implementation - Version 2

import math
import sys

def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def subtract(a, b):
    """Subtract b from a and return the result."""
    return a - b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide a by b and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

def power(a, b):
    """Calculate a raised to the power of b."""
    return a ** b

def square_root(a):
    """Calculate the square root of a."""
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number!")
    return math.sqrt(a)

def show_help():
    """Display help information for the calculator."""
    print("\nCalculator Operations:")
    print("  add - Add two numbers")
    print("  subtract - Subtract second number from first")
    print("  multiply - Multiply two numbers")
    print("  divide - Divide first number by second")
    print("  power - Raise first number to the power of second")
    print("  sqrt - Calculate square root of a number")
    print("  help - Show this help message")
    print("  exit - Exit the calculator\n")

def main():
    print("Enhanced Calculator - v2.0")
    print("Type 'help' for available operations or 'exit' to quit")
    
    while True:
        try:
            user_input = input("\nEnter operation: ").strip().lower()
            
            if user_input == "exit":
                print("Exiting calculator. Goodbye!")
                sys.exit(0)
            
            if user_input == "help":
                show_help()
                continue
                
            if user_input == "sqrt":
                a = float(input("Enter number: "))
                result = square_root(a)
                print(f"Square root of {a} = {result}")
                continue
                
            a = float(input("Enter first number: "))
            
            if user_input not in ["add", "subtract", "multiply", "divide", "power"]:
                print(f"Unknown operation: {user_input}")
                print("Type 'help' to see available operations")
                continue
                
            b = float(input("Enter second number: "))
            
            if user_input == "add":
                result = add(a, b)
                print(f"{a} + {b} = {result}")
            elif user_input == "subtract":
                result = subtract(a, b)
                print(f"{a} - {b} = {result}")
            elif user_input == "multiply":
                result = multiply(a, b)
                print(f"{a} × {b} = {result}")
            elif user_input == "divide":
                result = divide(a, b)
                print(f"{a} ÷ {b} = {result}")
            elif user_input == "power":
                result = power(a, b)
                print(f"{a} ^ {b} = {result}")
                
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 