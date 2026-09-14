from flask import Flask
from config import Config 
from extensions import db
from flask_migrate import Migrate
from models import User,RoomType,Room,Bill,Booking,Hotel
from routes import routes
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate=Migrate(app,db)
    app.register_blueprint(routes)
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("Database connected successfully!")
        except Exception as e:
            print("Database connection failed!")
            print(e)
    return app
app=create_app()
if __name__=="__main__":
    app.run(debug=True)