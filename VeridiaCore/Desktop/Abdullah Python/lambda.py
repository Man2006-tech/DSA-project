# # Regular function
# def square(x):
#     return x*x

# add=lambda a,b:a-b

# print (square(5))
# print (add(2,3))

# numbers = [1, 2, 3, 4]
# squares = list(map(lambda x: x**2, numbers))
# print(squares)       # ➔ [1, 4, 9, 16]

# numbers = [1, 2, 3, 4, 5, 6]
# odds = list(filter(lambda x: x % 2 != 0, numbers))
# print(odds)          # ➔ [1, 3, 5]

# students = [("Ali", 25), ("Sara", 20), ("John", 22)]
# sorted_students = sorted(students, key=lambda x: x[1])
# print(sorted_students)  
# # ➔ [('Sara', 20), ('John', 22), ('Ali', 25)]
students=[("Ehsan",21),("Gujjar",20),("Ali Sher",25)]
sorted_students=sorted(students,key=lambda x:x[1])
print(sorted_students)

array=[1,3,2,4,5,6,7,8]
filtered_array=list(filter(lambda x: x % 2 !=0,array))
print(filtered_array)


