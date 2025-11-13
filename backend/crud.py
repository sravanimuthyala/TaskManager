from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Task
from schemas import TaskCreate, TaskUpdate

def get_tasks(db: Session):
    return db.query(Task).all()

def create_task(db: Session, task: TaskCreate):
    new_task = Task(title=task.title)
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create task")

def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    # modern way to get by PK
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed

    try:
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update task")

def delete_task(db: Session, task_id: int):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete task")