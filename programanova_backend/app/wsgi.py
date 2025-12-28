from main import app

if __name__ == "__main__":
    app.run()
    
from app.main import app

# Railway / Gunicorn entrypoint
application = app
