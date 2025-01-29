from datetime import datetime
from flask import Blueprint, abort, request, jsonify

# from app.celery_tasks.celery_tasks.make_celery import create_task
from celery.result import AsyncResult

celery_tasks = Blueprint("celery_tasks", __name__)


# @celery_tasks.route("/create_task", methods=["POST"])
# def create():
#     content = request.json
#     task_type = content["type"]
#     task = create_task.delay(task_type)
#     return jsonify({"task_id", task.id})


@celery_tasks.route("/get_task/<task_id>", methods=["GET"])
def get_task(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return jsonify(result), 200
