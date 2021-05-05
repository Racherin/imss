from app import app

"""
This file includes our gunicorn support for deploy this project on heroku.
"""

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)