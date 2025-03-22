#!/usr/bin/env python3
# A greeting program - Fixed version

def greet(name, time_of_day):
    """
    Generate a greeting based on the time of day.
    
    Args:
        name (str): The name of the person to greet
        time_of_day (str): 'morning', 'afternoon', or 'evening'
    
    Returns:
        str: Appropriate greeting
    """
    # Bug fixed: Changed 'moring' to 'morning'
    if time_of_day == "morning":
        return f"Good morning, {name}!"
    elif time_of_day == "afternoon":
        return f"Good afternoon, {name}!"
    elif time_of_day == "evening":
        return f"Good evening, {name}!"
    else:
        return f"Hello, {name}!"

def main():
    print("Welcome to the Greeting Program!")
    
    name = input("What is your name? ")
    time = input("What time of day is it (morning/afternoon/evening)? ").lower()
    
    message = greet(name, time)
    print(message)

if __name__ == "__main__":
    main() 