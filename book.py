from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Connect to MongoDB
client = MongoClient('mongodb+srv://Game:<Pass>@cluster0.poeio.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', server_api=ServerApi('1'))
db = client['bookstore']
collection = db['books']

# Sample data (optional, for initialization)
sample_books = [
    {"id": 1, "title": "The Let Them Theory: A Life-Changing Tool That Millions of People Can't Stop Talking About", "author": "Mel Robbins", "image_url": "https://images-na.ssl-images-amazon.com/images/I/91I1KDnK1kL._AC_UL381_SR381,381_.jpg"},
    {"id": 2, "title": "Forgotten Home Apothecary : 250 Powerful Remedies at Your Fingertips", "author": "Dr. Nicole Apelian", "image_url": "https://images-na.ssl-images-amazon.com/images/I/91-E86oM2IL._AC_UL381_SR381,381_.jpg"},
    {"id": 3, "title": "Seven Things You Can't Say About China", "author": "Tom Cotton", "image_url": "https://images-na.ssl-images-amazon.com/images/I/81+mN748qkL._AC_UL381_SR381,381_.jpg"},
    {"id": 4, "title": "Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones", "author": "James Clear", "image_url": "https://images-na.ssl-images-amazon.com/images/I/81ANaVZk5LL._AC_UL381_SR381,381_.jpg"}
]

# Initialize MongoDB with sample data (optional)
if collection.count_documents({}) == 0:  # Check if the collection is empty
    collection.insert_many(sample_books)  # Insert sample data

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Create (POST) operation
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()

    # Generate a new ID
    new_id = collection.count_documents({}) + 1

    new_book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "image_url": data["image_url"]
    }

    # Insert the new book into MongoDB
    collection.insert_one(new_book)
    return jsonify(new_book), 201

# Read (GET) operation - Get all books
@app.route('/books', methods=['GET'])
@cross_origin()
def get_all_books():
    books_from_db = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id field
    return jsonify({"books": books_from_db})

# Read (GET) operation - Get a specific book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = collection.find_one({"id": book_id}, {"_id": 0})  # Exclude MongoDB's _id field
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

# Update (PUT) operation
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    result = collection.update_one({"id": book_id}, {"$set": data})
    if result.matched_count > 0:
        updated_book = collection.find_one({"id": book_id}, {"_id": 0})
        return jsonify(updated_book)
    else:
        return jsonify({"error": "Book not found"}), 404

# Delete operation
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = collection.delete_one({"id": book_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Book deleted successfully"})
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)