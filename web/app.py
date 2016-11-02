"""

Entry for the docker container running the Flask app.

"""

if __name__ == '__main__':
    from web import app
    app.run(debug=True, host='0.0.0.0')
    from web import views, models