class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # points to next node
        self.prev = None  # points to previous node



class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def insert_at_beginning(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            return

        # 1️⃣ Link new node to old head
        new_node.next = self.head
        self.head.prev = new_node

        # 2️⃣ Move head to new node
        self.head = new_node

    def print_forward(self):
        itr = self.head
        while itr:
            print(itr.data, end=" ⇄ ")
            itr = itr.next
        print("None")


    def add_at_end(self,data):
        new_node=Node(data)
        if not self.head:
            self.head=new_node
            return
            # self.head.next=self.head

      
        itr=self.head     
        while itr.next:
            itr=itr.next

        
        itr.next=new_node
        new_node.prev=itr


    # def print_forward(self)    :
    #     itr=self.head

    #     while itr:
    #         print(itr.data, end=" ⇢ ")
    #         last = itr  # Save last node
    #         itr = itr.next
    #     print("None")
    #     return last 
             

dll=DoublyLinkedList() 
dll.add_at_end("1234")
dll.add_at_end("5678")
dll.add_at_end("5678")
dll.add_at_end("5678")

dll.add_at_end("9")
dll.print_forward()
