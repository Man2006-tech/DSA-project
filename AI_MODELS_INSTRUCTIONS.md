
VERIDIA SEARCH - AI MODELS SETUP
================================

To enable "Semantic Search" (Smart AI Search), you need the "GloVe" model file.
The download is a ZIP file containing MULTIPLE versions (sizes). 

YOU ONLY NEED THE SMALLEST ONE.

HOW TO FIX "Embeddings file not found":
---------------------------------------

1.  Download the **GloVe** model file (glove.6B.zip).
    Link: https://nlp.stanford.edu/data/glove.6B.zip
    (Size: ~822MB ZIP)

2.  Extract the ZIP file.
    You will see 4 text files:
    - glove.6B.50d.txt   (<-- USE THIS ONE, it is small and fast)
    - glove.6B.100d.txt
    - glove.6B.200d.txt
    - glove.6B.300d.txt

3.  Take **`glove.6B.50d.txt`** and rename it to **`glove.txt`**.

4.  Move **`glove.txt`** into the **`VeridiaCore`** folder.
    (Inside `Search-Engine/VeridiaCore/`).

5.  Restart the Search Engine (`run_veridia.bat`).

RESULT:
-------
The warning will disappear, and Semantic Search will work!
