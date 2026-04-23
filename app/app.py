from flask import Flask 
import os

# Pulls from system environment, defaults to None if not found in system
# Rename 'password' to 'app_credentials' or 'env_password'
#app_credentials = os.environ.get("APP_PASSWORD")
 
app = Flask(__name__) 
@app.route("/")
 
def home(): 
	#secret = os.getenv("APP_SECRET") 
	return f"Hello, The Application is running securely"
 
if __name__ == "__main__": 
	host = os.environ.get("FLASK_HOST", "0.0.0.0") # nosec B104
	app.run(host=host, port=5000) # nosec B104
