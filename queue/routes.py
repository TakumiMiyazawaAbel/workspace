from flask import Blueprint, jsonify, request
from celery.result import AsyncResult

task_bp = Blueprint('tasks', __name__)

_celery = None
_tasks = None


def init_routes(celery, tasks):
    """ルートの初期化（Celeryインスタンスとタスクを設定）"""
    global _celery, _tasks
    _celery = celery
    _tasks = tasks


@task_bp.route('/')
def index():
    return jsonify({
        'message': 'Flask + Celery 非同期タスク API',
        'endpoints': {
            '/task/add': 'POST - 数値の加算タスクを実行',
            '/task/long/<duration>': 'POST - 長時間タスクを実行',
            '/task/email': 'POST - メール送信タスクを実行',
            '/task/<task_id>': 'GET - タスクのステータスを確認'
        }
    })


@task_bp.route('/task/add', methods=['POST'])
def create_add_task():
    data = request.get_json() or {}
    x = data.get('x', 10)
    y = data.get('y', 20)
    task = _tasks['add_numbers'].delay(x, y)
    return jsonify({'task_id': task.id, 'status': 'submitted'}), 202


@task_bp.route('/task/long/<int:duration>', methods=['POST'])
def create_long_task(duration: int):
    task = _tasks['long_running_task'].delay(duration)
    return jsonify({'task_id': task.id, 'status': 'submitted'}), 202


@task_bp.route('/task/email', methods=['POST'])
def create_email_task():
    data = request.get_json() or {}
    to = data.get('to', 'test@example.com')
    subject = data.get('subject', 'テストメール')
    body = data.get('body', 'これはテストメールです')
    task = _tasks['send_email_task'].delay(to, subject, body)
    return jsonify({'task_id': task.id, 'status': 'submitted'}), 202


@task_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=_celery)

    if task.state == 'PENDING':
        response = {'state': task.state, 'status': '待機中または存在しないタスク'}
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': '実行中'
        }
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result, 'status': '完了'}
    else:
        response = {'state': task.state, 'status': str(task.info)}

    return jsonify(response)
