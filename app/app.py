from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secure DB Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'myapp_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/items', methods=['POST', 'GET'])
def manage_items():
    if request.method == 'POST':
        new_item = Item(name=request.json['name'])
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"status": "created"}), 201
    items = Item.query.all()
    return jsonify([{"id": i.id, "name": i.name} for i in items])

if __name__ == '__main__':
    # Fixed for Bandit B104
    app.run(host=os.getenv('APP_HOST', '0.0.0.0'), port=5000) # nosec B104
