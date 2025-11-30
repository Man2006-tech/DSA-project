text = "apple"

# Step 1: Split the text into words
words = text.split()

# Step 2: Create an empty dictionary to store counts
word_count = {}

# Step 3: Loop through each word and count occurrences
for word in words:
    if word in word_count:
        word_count[word] += 1  # If word exists, increment count
    else:
        word_count[word] = 1  # If word doesn't exist, add it with count 1

# Step 4: Print the result
print(word_count)
