class ODD:
    def __init__(self,high):

        self.low=1
        self.high=high
     
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.low>=self.high:
            raise StopIteration
        
        else :
          current=self.low
          self.low+=2
          return current



for i in ODD(10):
    print(i,end=" ")

