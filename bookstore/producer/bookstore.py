from flask import Flask, render_template, jsonify, request
from kafka import KafkaProducer
import json

app = Flask(__name__)

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Sample book data
BOOKS = [
    {"id": 1, "title": "1984", "author": "George Orwell", "description": "Dystopian novel.", "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTg9twOHNjnyPPgQz4aQ55vFRseeJkbGAwHHw4uMYQH4BjGDnrjAX9tNVOSmK36Wc6ngDM&usqp=CAU"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "description": "Classic of modern American literature.", "image_url": "https://images.booksense.com/images/183/798/9780062798183.jpg"},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "description": "Novel about the American dream.", "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTz_MgbPqvi2XljZ3pTmKYmISoSeaeBu_wcKBJQfW5cho7zbDMxrGQEuTbe1gfwM2TpUwk&usqp=CAU"},
    {"id": 4, "title": "Moby Dick", "author": "Herman Melville", "description": "Epic tale of a sea captains obsession.", "image_url": "https://www.accartbooks.com/app/uploads/books/9788854420564-04-2.jpg"},
]

@app.route('/')
def index():
    return render_template('bookstore.html', books=BOOKS)

@app.route('/track-event', methods=['POST'])
def track_event():
    try:
        event_data = request.get_json()
        producer.send('bookstore_events', event_data)
        producer.flush()
        return jsonify({"status": "success", "message": "Event tracked successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
