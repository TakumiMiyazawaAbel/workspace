import time


def register_tasks(celery):
    """Celeryタスクを登録"""

    @celery.task(bind=True, name='tasks.long_running_task')
    def long_running_task(self, duration: int):
        """時間のかかるタスクのサンプル"""
        for i in range(duration):
            time.sleep(1)
            self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': duration})
        return {'status': 'completed', 'result': f'{duration}秒のタスクが完了しました'}

    @celery.task(name='tasks.add_numbers')
    def add_numbers(x: int, y: int):
        """シンプルな計算タスク"""
        time.sleep(2)
        return x + y

    @celery.task(name='tasks.send_email_task')
    def send_email_task(to: str, subject: str, body: str):
        """メール送信タスクのサンプル（実際の送信はしない）"""
        time.sleep(3)
        return {'status': 'sent', 'to': to, 'subject': subject}

    return {
        'long_running_task': long_running_task,
        'add_numbers': add_numbers,
        'send_email_task': send_email_task,
    }
