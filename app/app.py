from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import socket

app = Flask(__name__)

# --- Database Configuration ---
# Fetching from env vars is best practice for security and K8s configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'myapp_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
password="Cyberpro@123"

# --- Database Model ---
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Initialize Database tables
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles both the view list and the add-item form."""
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_item = Item(name=name)
            db.session.add(new_item)
            db.session.commit()
        return redirect(url_for('index'))
    
    items = Item.query.all()
    # socket.gethostname() allows you to identify which Pod is responding
    return render_template('index.html', items=items, pod=socket.gethostname())

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Handles editing an existing item."""
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)

@app.route('/delete/<int:id>')
def delete(id):
    """Handles deleting an item."""
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Binding to 0.0.0.0 is required for K8s ingress traffic.
    # '# nosec B104' is a Bandit exception for this necessary configuration.
    app.run(host='0.0.0.0', port=5000)  # nosec B104
