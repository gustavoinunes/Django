from waitress import serve
import sohome.wsgi

if __name__ == "__main__":
    serve(sohome.wsgi.application, host='127.0.0.1', port=8000)