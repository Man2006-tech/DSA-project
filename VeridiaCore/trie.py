class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0  # To rank suggestions

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, frequency=0):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.frequency = frequency

    def search_prefix(self, prefix, limit=5):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # DFS to find all words from this node
        suggestions = []
        self._dfs(node, prefix, suggestions)
        
        # Sort by frequency (descending) and length (ascending) for relevance
        suggestions.sort(key=lambda x: (-x[1], len(x[0])))
        
        return [word for word, freq in suggestions[:limit]]

    def _dfs(self, node, prefix, suggestions):
        if node.is_end_of_word:
            suggestions.append((prefix, node.frequency))
        
        for char, child_node in node.children.items():
            self._dfs(child_node, prefix + char, suggestions)
