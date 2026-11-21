# Local development entry point. The backend lives in api/index.py so the same
# code runs as a Vercel Python function in production.
from api.index import app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
