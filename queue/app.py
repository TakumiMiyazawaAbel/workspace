from flask import Flask

from config import Config
from celery_app import make_celery
from tasks import register_tasks
from routes import task_bp, init_routes

app = Flask(__name__)
app.config.from_object(Config)

celery = make_celery(app)
tasks = register_tasks(celery)

init_routes(celery, tasks)
app.register_blueprint(task_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
