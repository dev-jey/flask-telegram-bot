from application.factory import create_app
import application

app = create_app(celery=application.celery)

if __name__ == "__main__":  
    app.run(debug=False)