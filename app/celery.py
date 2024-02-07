from celery.signals import task_postrun

@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
  update_celery_task_status_socketio(task_id)
  
  
  