class Person:
    def __init__(self,name):
          
     self.name=name
    def __str__(self):
        return f"{self.name} on the way"
    
    def __repr__(self):
        return f"Person ('{self.name}')"
    
    def __len__(self):
       return len(self.name)
    
ehsan=Person("Chaudhary")

gujjar=eval(repr(ehsan))
# print(str(ehsan))
print(repr(ehsan))
print(gujjar)
print(gujjar.name)
print(len(ehsan))


