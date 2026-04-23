from flask import Flask 
import os

# Pulls from system environment, defaults to None if not found in system
password = os.environ.get("APP_PASSWORD")
 
app = Flask(__name__) 
@app.route("/")
 
def home(): 
	secret = os.getenv("APP_SECRET") 
	return f"Hello, Secret is {secret}"
 
if __name__ == "__main__": 
	host = os.environ.get("FLASK_HOST", "127.0.0.1")
	app.run(host=host, port=5000) 
