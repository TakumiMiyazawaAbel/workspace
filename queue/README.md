# Flask + Celery 非同期タスク実行環境

FlaskアプリケーションでCeleryを使った非同期タスク処理を行うサンプルプロジェクトです。

## 構成

- **Flask**: WebアプリケーションフレームワークREST API
- **Celery**: 非同期タスクキュー
- **Redis**: メッセージブローカー & 結果バックエンド
- **Flower**: Celeryタスクモニタリングダッシュボード

## 起動方法

```bash
# Docker Composeで全サービスを起動
docker compose up --build

# バックグラウンドで起動する場合
docker compose up --build -d
```

## アクセスURL

| サービス | URL |
|---------|-----|
| Flask API | http://localhost:5000 |
| Flower (タスクモニター) | http://localhost:5555 |

## API エンドポイント

### タスク作成

**1. 数値の加算タスク**
```bash
curl -X POST http://localhost:5000/task/add \
  -H "Content-Type: application/json" \
  -d '{"x": 10, "y": 20}'
```

**2. 長時間実行タスク（進捗付き）**
```bash
# 10秒間のタスクを実行
curl -X POST http://localhost:5000/task/long/10
```

**3. メール送信タスク（サンプル）**
```bash
curl -X POST http://localhost:5000/task/email \
  -H "Content-Type: application/json" \
  -d '{"to": "user@example.com", "subject": "テスト", "body": "本文"}'
```

### タスクステータス確認

```bash
curl http://localhost:5000/task/<task_id>
```

**レスポンス例（実行中）:**
```json
{
  "state": "PROGRESS",
  "current": 3,
  "total": 10,
  "status": "実行中"
}
```

**レスポンス例（完了）:**
```json
{
  "state": "SUCCESS",
  "result": {"status": "completed", "result": "10秒のタスクが完了しました"},
  "status": "完了"
}
```

## カスタムタスクの追加方法

`app.py` に新しいタスクを追加できます：

```python
@celery.task
def my_custom_task(param1, param2):
    # 時間のかかる処理
    import time
    time.sleep(5)
    return {"result": "処理完了"}
```

エンドポイントを追加：

```python
@app.route('/task/custom', methods=['POST'])
def create_custom_task():
    data = request.get_json() or {}
    task = my_custom_task.delay(data.get('param1'), data.get('param2'))
    return jsonify({'task_id': task.id}), 202
```

## 停止方法

```bash
docker compose down

# ボリュームも削除する場合
docker compose down -v
```

## ローカル開発（Docker なし）

```bash
# Redisをインストール・起動
# Ubuntu/Debian
sudo apt install redis-server
sudo service redis-server start

# 依存関係インストール
pip install -r requirements.txt

# Celery Worker起動（別ターミナル）
celery -A app.celery worker --loglevel=info

# Flask起動
python app.py
```
