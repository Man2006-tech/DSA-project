''''x = 5          # Integer
name = "Alice" # String
price = 19.99  # Float
is_active = True # Boolean
print("Hello World")
age = 14

if age >= 18:
 print("Adult")
elif age >= 13:
 print("Teen")
else:
    print("Child")
    name = input("Enter your name: ")
print(f"Hi, {name}")'''

""""for i in range (4,7):
 print(i)"""

""""def add(a,b):
    return a+b

result=add(2,3)
print(f"{result}")"""

# def add(a,b=3):
#     return a+b 

# result=add(4)
# print(result)

# my_list=[1,"Ehsan"]
# print(my_list[1])
# print("Last Item:", my_list[-1])
# my_list.append(60)
# print("After Appending 60:", my_list)
# my_list.insert(-6,222)
# print(my_list)
# for item in my_list:
#     print(item, end=" ")
# nested_mylist=[[1,22],[11,111],[2,4]]
# print(nested_mylist[2][1])

# for item in nested_mylist:

#      for inner_item in item:

#       print(inner_item)
# d = {"a": 1, "b": 2}
# print(d)  # {'a': 2}
# Example: Preprocessing string data for an AI model
# def preprocess_data(raw_data):
#     # List of string inputs (e.g., from a CSV file)
#     cleaned_data = []
#     for item in raw_data:
#         try:
#             # Explicitly cast string to float for numerical processing
#             numerical_value = float(item)
#             cleaned_data.append(numerical_value)
#         except ValueError:
#             print(f"Cannot convert {item} to float. Skipping.")
#     return cleaned_data

# # Sample data: strings representing feature values
# raw_data = ["10.5", "20", "invalid", "15.75"]
# numerical_data = preprocess_data(raw_data)
# print("Processed Data:", numerical_data)  # Output: Processed Data: [10.5, 20.0, 15.75]
# try:
#     x = 10 / 2
# except ZeroDivisionError:
#     print("Error!")
# else:
#     print("No error. Result:", x)
