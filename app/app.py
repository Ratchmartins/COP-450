from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import socket
import time

app = Flask(__name__)

# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------
DB_USER = os.getenv('DB_USER', 'asanti')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST', 'pg-asanti-rw')  # FIXED: CNPG primary service
DB_NAME = os.getenv('DB_NAME', 'myapp_db')

if not DB_PASS:
    raise Exception("DB_PASS environment variable is required")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# DATABASE MODEL
# -----------------------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# -----------------------------
# SAFE DB INITIALIZATION
# (prevents CrashLoopBackOff)
# -----------------------------
def init_db_with_retry(retries=10, delay=5):
    """
    Waits for DB to be ready before creating tables.
    Prevents startup crash if DB is not ready.
    """
    for i in range(retries):
        try:
            with app.app_context():
                db.create_all()
                db.session.execute(text("SELECT 1"))
            print("✅ Database is ready")
            return
        except Exception as e:
            print(f"⏳ DB not ready (attempt {i+1}/{retries}): {e}")
            time.sleep(delay)

    raise Exception("❌ Database not reachable after retries")

# Initialize DB safely
init_db_with_retry()

# -----------------------------
# HEALTH CHECK (K8s probes)
# -----------------------------
@app.route('/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "pod": socket.gethostname()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# -----------------------------
# MAIN ROUTE
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_item = Item(name=name)
            db.session.add(new_item)
            db.session.commit()
        return redirect(url_for('index'))

    items = Item.query.all()
    return render_template('index.html', items=items, pod=socket.gethostname())

# -----------------------------
# EDIT ITEM
# -----------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)

# -----------------------------
# DELETE ITEM
# -----------------------------
@app.route('/delete/<int:id>')
def delete(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

# -----------------------------
# START APP
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
