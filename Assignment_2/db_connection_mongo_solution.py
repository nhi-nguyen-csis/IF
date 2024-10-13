from pymongo import MongoClient
import string # remove punctuation 
import datetime

def connectDataBase():

    # Creating a database connection object using pymongo

    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:

        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]

        return db

    except:
        print("Database not connected successfully")

def remove_punctuation(text):
    """Helper function: Removes punctuation from a string."""
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def count_chars(word):
    """Helper function: Count number of characters in a word 
    OR number of characters in a text."""
    count = 0
    for char in word:
        if char.isalnum():
            count += 1
    return count

def count_word_frequencies(target_word, text):
    """Helper function: Count number of characters in a word 
    OR number of characters in a text."""
    count = 0
    for word in text:
        if word == target_word:
            count += 1
    return count

def create_terms(text):
    """Helper function: Return terms array of 
    each term object in the text"""
    text = remove_punctuation(text.lower()).split()
    terms= []
    seen = set()
    for word in text:
        if word in seen:
            continue
        seen.add(word)
        cache = {}
        cache["term"] = word
        cache["count"] = count_word_frequencies(word, text)
        cache["num_chars"] = count_chars(word)
        terms.append(cache)
    return terms

def createDocument(documents, docId, docText, docTitle, docDate, docCat):
    # Value to be inserted
    doc = {"_id": docId, 
           "title": docTitle,
           "text": docText,
           "num_chars": count_chars(docText),
           "date": {"$date": datetime.datetime.strptime(docDate, "%Y-%m-%d")},
           "category": docCat,
            "terms": create_terms(docText)
           }
    # Insert the document
    documents.insert_one(doc)

def deleteDocument(documents, docId):
    documents.delete_one({"_id": docId})

def updateDocument(documents, docId, docText, docTitle, docDate, docCat):
    # doc fields to be updated
    doc = {"$set": {"_id": docId, 
           "title": docTitle,
           "text": docText,
           "num_chars": count_chars(docText),
           "date": {"$date": datetime.datetime.strptime(docDate, "%Y-%m-%d")},
           "category": docCat,
            "terms": create_terms(docText)
           } }

    # Updating the user
    documents.update_one({"_id": docId}, doc)

def getIndex(documents):
    # creating a document for each message
    pipeline = [
    {"$unwind": "$terms"},  # Unwind the terms array
    {"$group": {
        "_id": "$terms.term",  # Group by the term
        "documents": {
            "$push": {
                "title": "$title",
                "count": "$terms.count"
            }
        }
    }},
    {"$sort": {"_id": 1}}  # Sort by term
]

    # Execute the aggregation
    results = documents.aggregate(pipeline)

    # Create the inverted index
    inverted_index = {}
    for result in results:
        term = result["_id"]
        entries = [f"{doc['title']}:{doc['count']}" for doc in result["documents"]]
        inverted_index[term] = ", ".join(entries)

    # return the inverted index
    return inverted_index