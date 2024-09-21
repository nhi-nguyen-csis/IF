#-------------------------------------------------------------------------
# AUTHOR: Nhi Nguyen
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 5180- Assignment #1
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#Importing some Python libraries
import csv
import math # for logarithm calculation
# import pandas as pd # output the result in a dataframe

documents = []

#Reading the data in a csv file
with open('collection.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for i, row in enumerate(reader):
         if i > 0:  # skipping the header
            documents.append (row[0])

'''
['I love cats and cats', '
She loves her dog', 
'They love their dogs and cat']
'''
# print(documents)

#Conducting stopword removal for pronouns/conjunctions. 
# Hint: use a set to define your stopwords.
#--> add your Python code here
stopWords = {"I", "and", "She", "her", "They", "their"}
for i in range(len(documents)):
    documents[i] = [word for word in documents[i].split() if word not in stopWords]


# #Conducting stemming. Hint: use a dictionary to map word variations to their stem.
# #--> add your Python code here
steeming = {"cats": "cat", "dogs": "dog", "loves": "love"}
for i in range(len(documents)):
    documents[i] = [steeming[word] if word in steeming else word for word in documents[i]]

# [['love', 'cat', 'cat'], ['love', 'dog'], ['love', 'dog', 'cat']]
# print(documents)

# #Identifying the index terms.
# #--> add your Python code here
terms = []
for document in documents:
    for word in document:
        if word not in terms:
            terms.append(word)

# print(terms) # ['love', 'cat', 'dog']

# helper function to compute tf for each term in the each document
def compute_tf(term, document):
    return document.count(term) / len(document)


# #Building the document-term matrix by using the tf-idf weights.
# #--> add your Python code here
docTermMatrix = []

# helper function to compute idf for each term in the collection
def compute_idf(term, documents):
    num_docs_containing_term = sum(1 for document in documents if term in document)
    return math.log10(len(documents) / (num_docs_containing_term))

for document in documents:
    doc_tfidf = []
    for term in terms:
      tf = compute_tf(term, document)
      idf = compute_idf(term, documents)
      doc_tfidf.append(tf * idf)
    docTermMatrix.append(doc_tfidf)
        

# #Printing the document-term matrix.
# #--> add your Python code here

print("Terms:", terms)
print("\nDocument-Term Matrix (TF-IDF):")
for i, row in enumerate(docTermMatrix):
    print(f"Document {i+1}: {row}")

# ---------- Uncomment the line below to display the result in a DataFrame ----------
# index = ["Doc 1", "Doc 2", "Doc 3"]
# df = pd.DataFrame(docTermMatrix, columns=terms, index=index)
# print(df)
