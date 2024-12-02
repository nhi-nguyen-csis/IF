from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from pymongo import MongoClient 
import pandas as pd

def connectDataBase():
    # Creating a database connection object using pymongo
    DB_NAME = "HW5"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

def save_terms_to_db(db, terms):
    terms_documents = db["terms_collection"]
    terms_documents.insert_many(terms)

def save_docs_to_dv(db, docs):
    docs_document = []
    for i, doc in enumerate(docs):
        docs_document.append({"_id": i+1, "content": doc })
    db["docs_collection"].insert_many(docs_document)



# List of documents
documents = [
    "After the medication, headache and nausea were reported by the patient.",
    "The patient reported nausea and dizziness caused by the medication.",
    "Headache and dizziness are common effects of this medication.",
    "The medication caused a headache and nausea, but no dizziness was reported."
]

queries = ["nausea and dizziness", "effects", "nausea was reported", "dizziness", "the medication"]


# Step 1: Generate unigrams, bigrams, and trigrams using CountVectorizer
vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 3)) 
X_docs = vectorizer.fit_transform(documents)

# Step 2: Generate the TF-IDF matrix
tfidf_transformer = TfidfTransformer()
X_tfidf = tfidf_transformer.fit_transform(X_docs)

# convert the queries set into a matrix based on the documents set index terms.
test_queries  = vectorizer.transform(queries)
print(f"test_queries = {test_queries}")

print("Count Vectorizer Test\n")
#retrieve the terms found in the corpora
count_tokens = vectorizer.get_feature_names_out()
print(pd.DataFrame(data = test_queries.toarray(),index = ['Q1','Q2', 'Q3', 'Q4', 'Q5'],columns = count_tokens))

# Step 3: Extract terms and their attributes
vocab = vectorizer.vocabulary_  # Vocabulary dictionary
terms_data = []

for term, pos in vocab.items():
    term_docs = []
    for doc_idx in range(len(documents)):
        # extract TF-IDF value for the term in this document
        tfidf_value = X_tfidf[doc_idx, pos] 
        # Include only if the term exists in this document
        if tfidf_value > 0:  
            term_docs.append(
                {"doc_id": doc_idx+1, # doc ID starting at 1
                 "tfidf": tfidf_value})      
    # Sort term_docs by TF-IDF value in descending order
    term_docs = sorted(term_docs, key=lambda x: x["tfidf"], reverse=True)
    # save the current term into the terms_data
    terms_data.append({
        "_id": len(terms_data)+1,  # Unique term ID
        "term": term,  # Term text
        "pos": pos,  # Position in vocabulary
        "docs": term_docs  # Documents containing the term
    })

# Step 4. Connect to the database
db = connectDataBase()

# Step 5: Save docs to database
save_docs_to_dv(db, documents)

# Step 6: Save terms to database
save_terms_to_db(db, terms_data)


# Step 4: Create a DataFrame for better visualization
terms_df = pd.DataFrame(terms_data)

# Display the results
print(terms_df.to_string(index=False))

