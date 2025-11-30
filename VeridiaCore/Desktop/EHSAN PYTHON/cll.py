# class Node:
#     def __init__(self, data):
#         self.data = data      # Song name
#         self.next = None      # Pointer to next song


# class CircularLinkedList:
#     def __init__(self):
#         self.head = None

#     def append(self, data):
#         """Add song at the end of the playlist"""
#         new_node = Node(data)
#         if not self.head:
#             self.head = new_node
#             self.head.next = self.head
#         else:
#             cur = self.head
#             while cur.next != self.head:
#                 cur = cur.next
#             cur.next = new_node
#             new_node.next = self.head

#     def prepend(self, data):
#         """Add song at the beginning of the playlist"""
#         new_node = Node(data)
#         if not self.head:
#             self.head = new_node
#             self.head.next = self.head
#         else:
#             cur = self.head
#             while cur.next != self.head:
#                 cur = cur.next
#             cur.next = new_node
#             new_node.next = self.head
#             self.head = new_node

#     def print_playlist(self):
#         """Print the current playlist"""
#         if not self.head:
#             print("Playlist is empty.")
#             return

#         cur = self.head
#         print("Playlist:")
#         while True:
#             print(cur.data, end=" → ")
#             cur = cur.next
#             if cur == self.head:
#                 break
#         print("(back to start)")

#     def play_songs(self, num_songs):
#         """Simulate playing songs continuously for a given number of times"""
#         if not self.head:
#             print("Playlist is empty.")
#             return

#         cur = self.head
#         print("\nPlaying songs:")
#         for _ in range(num_songs):
#             print(f"Playing: {cur.data}")
#             cur = cur.next


# # 🔗 Create and Test the Playlist
# playlist = CircularLinkedList()
# playlist.append("Song A")
# playlist.append("Song B")
# playlist.append("Song C")

# playlist.prepend("Intro Song")

# playlist.print_playlist()

# playlist.play_songs(7)  # Play 7 songs to show the circular nature


class Node:
    def __init__(self,data):
        self.data=data
        self.next=None


class CLL:

    def __init__(self):
        self.head=None


    def append(self,data): 

        new_node= Node(data)    

        if not self.head:
            self.head=new_node
            self.head.next=self.head

        else:
            curr=self.head
             
            while curr.next!=self.head:
                curr=curr.next
            curr .next=new_node
            new_node.next=self.head

    def print_playlist(self):
        if not self.head:
            print("The playlist is empty")
            return 
        curr=self.head
        print("Playlist")
        while True:
         print(curr.data,end="-->")
         curr=curr.next
         if curr==self.head:
          break
        print("(back to start)",curr.data)
    def prepend(self, data):
        """Add song at the beginning of the playlist"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.head.next = self.head
        else:
            cur = self.head
            while cur.next != self.head:
                cur = cur.next
            cur.next = new_node
            new_node.next = self.head
            self.head = new_node
           

n=CLL()
n.append(10)
n.append(20)
n.append(30)
# n.prepend(40)
n.print_playlist()

                


            



        
        