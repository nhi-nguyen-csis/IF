from bs4 import BeautifulSoup 
from pymongo import MongoClient 
import re # find html and shtml in the retrieved links

def connectDataBase():
    # Creating a database connection object using pymongo
    DB_NAME = "CS_CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

def save_to_db(db, faculty):
    prof_documents = db["professors"]
    prof_documents.insert_many(faculty)

def extract_email_web(p_tag, label):
    href_tag = p_tag.find('a', href=re.compile(label))
    return href_tag.get_text(strip=True) if href_tag else None

def extract_fields(soup):
    faculty = []
    for h2_tag in soup.find_all("h2")[1:]:
        person = {}
        if not h2_tag: continue
        # 5a. Extracting Name
        person['name'] = h2_tag.get_text().strip()
        # Find the next sibling that is a <p> tag to extract the other fields
        p_tag = h2_tag.find_next_sibling('p')
        # 5b. Extracting: Title, Office, Phone number
        def extract_field(label):
            strong_tag = p_tag.find('strong', string=lambda s: label in s)
            field =  strong_tag.next_sibling.strip(": ") if strong_tag and strong_tag.next_sibling else None
            return field.replace('\xa0', '') if field else None
        person["title"] = extract_field("Title")
        person["office"] = extract_field("Office")
        person["phone"] = extract_field("Phone")
        # 5c. Extracting: Email and Website
        person['email'] = extract_email_web(p_tag, '^mailto:')
        person['web'] = extract_email_web(p_tag, '.*http')
        # 5d. Adding all extracting into from the person into the faculty list 
        faculty.append(person)
    return faculty

def parsing_faculty():
    # 1. Connect to the database
    db = connectDataBase()
    # 2. Access the collection 
    documents = db["CS_CPP_pages"]
    # 3. Find the target page in the collection's database
    TARGET_URL = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
    page = documents.find_one({"url": TARGET_URL})
    # 4. Extract the target page's html
    soup = BeautifulSoup(page['html'], 'html.parser')
    # 5. Starting parsing
    faculty = extract_fields(soup)
    # 6. Create a new collection and save it into the database
    save_to_db(db, faculty)

if __name__ == "__main__":
    parsing_faculty()