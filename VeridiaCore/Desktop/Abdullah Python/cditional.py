# def create_user_profile(name, age:int, occupation="Student", interests=None): # Use None as default
#     """
#     Creates a user profile with optional interests.

#     Args:
#         name (str): The user's name (required).
#         age (int): The user's age (required).
#         occupation (str, optional): The user's occupation (defaults to "Student").
#         interests (list, optional): A list of the user's interests (defaults to None).
#     """
#     if interests is None:  # Initialize if None
#         interests = [] 

#     profile = {
#         "name": name,
#         "age": age,
#         "occupation": occupation,
#         "interests": interests
#     }

#     return profile

# # Usage
# user1 = create_user_profile("Alice", 25, "Software Engineer", ["Coding", "Hiking"])
# user2 = create_user_profile("Bob", 18)  # Uses default occupation and no interests
# user3 = create_user_profile("Carol", 30, interests=["Gardening", "Reading"])

# print(user1)
# print(user2)
# print(user3)

# File: mymodule.py

# def greet(name):
#     return f"Hello, {name}!"

# def add(a, b):
#     return a + b



# PI = 3.14159

# add(2,PI) 

my_dict = {
    (1, 2, 3): "Tuple key",  # tuple is immutable
    frozenset([4, 5, 6]): "Frozenset key",
    "name": "Ehsan",         # string is immutable
    42: "Number key"
}

print(my_dict[(1, 2, 3)])  # Output: Tuple key

# key = [1, 2, 3]  # mutable list
# my_dict = {key: "This won't work"}
my_dict={(1,2,3):"Tuple key",frozenset([4,5,6,2]):"Set key"}
print(my_dict[frozenset([4, 5, 6,2])])  # Output: Tuple key
