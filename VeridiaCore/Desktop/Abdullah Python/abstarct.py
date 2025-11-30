from abc import ABC,abstractmethod


class Animal(ABC):
   @abstractmethod
   def speak(self):
    pass
   def animal(self):
      print("oh animal")
   
class Dog(Animal):
  @abstractmethod
  def speak(self):
    pass
  
  @abstractmethod
  def play(self):
    pass
  def name(self):
   print("Pitbull")
  
class Cat(Dog):
   def speak(self):
    print(  "Meow")
   def play(self):
      print("Cat show")

c=Cat()
c.speak()
c.play()
c.name()
c.animal()

