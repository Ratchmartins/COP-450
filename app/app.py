from flask import Flask 
import os
 
app = Flask(__name__) 
@app.route("/")

password = "12345"
 
def home(): 
	secret = os.getenv("APP_SECRET") 
	return f"Hello, Secret is {secret}"
 
if __name__ == "__main__": 
	app.run(host="0.0.0.0", port=5000) 
