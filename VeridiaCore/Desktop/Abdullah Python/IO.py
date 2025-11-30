# file=open("example.txt","r")
# content=file.read()
# print(content)
# Use the complete path to your file
file_path = r"C:\Users\Ehsan Ullah\OneDrive\Documents\example.txt"
# with open(file_path, "a") as file:
#  file.write("This text will be appended to the file\n")
#  file.write("You can add multiple lines like this\n")

# with open(file_path ,"r") as file:
#  content=file.read()
# print(content)

with open(file_path,"w") as file:
    
         file.write("O Shera!Kr mehnat")
 
with open(file_path ,"r") as file: 
   content=file.read()
print(content)
