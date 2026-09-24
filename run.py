from app import create_app

app = create_app()

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(host='0.0.0.0', port=8443, debug=True, ssl_context=('cert.pem', 'key.pem'))
=======
    app.run(host='0.0.0.0', port=8443, debug=True, ssl_context=('cert.pem', 'key.pem'))
>>>>>>> c3aaac468f8a76dc60a81d1899c88179c818a294
