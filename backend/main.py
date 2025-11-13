# -----------------------------------------
# IMPORTS
# -----------------------------------------
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os, json


# -----------------------------------------
# ENV + OPENAI SETUP
# -----------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("❌ OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------------------
# DATABASE SETUP
# -----------------------------------------
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# -----------------------------------------
# DB MODEL
# -----------------------------------------
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


# -----------------------------------------
# SCHEMAS (Pydantic v2 Clean)
# -----------------------------------------
class Task(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: bool = False


class TaskDB(Task):
    id: int
    model_config = ConfigDict(from_attributes=True)   # FIX for Pydantic v2


class TaskPrompt(BaseModel):
    prompt: str


# -----------------------------------------
# FASTAPI + CORS FIX
# -----------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# DB DEPENDENCY
# -----------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# CRUD ROUTES
# -----------------------------------------
@app.get("/tasks", response_model=List[TaskDB])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()


@app.post("/tasks", response_model=TaskDB)
def create_task(task: Task, db: Session = Depends(get_db)):
    new_task = TaskModel(**task.model_dump())   # FIXED .dict() warning
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskDB)
def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    data = task.model_dump()   # FIXED

    t.title = data["title"]
    t.description = data["description"]
    t.completed = data["completed"]

    db.commit()
    db.refresh(t)
    return t


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(t)
    db.commit()
    return {"message": "Task deleted"}


# -----------------------------------------
# AI — RECOMMENDATIONS
# -----------------------------------------
@app.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    tasks = db.query(TaskModel).all()

    if not tasks:
        return {"message": "No tasks found"}

    summary = "\n".join([f"- {t.title} (Done: {t.completed})" for t in tasks])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful task management assistant"},
            {"role": "user", "content":(
                     f"Here are my current tasks:\n{summary}\n\n"
                    "Please provide recommendations on which tasks to prioritize and next steps. "
                    "Format your response clearly: "
                    "- Use numbered tasks. "
                    "- Use bold text for priorities. "
                    "- Include bullet points for actionable next steps. "
                    "- Add a short final recommendation. "
                    "Return as plain text with line breaks so it's easy to read."
            )},
        ]
    )

    return {"recommendation": response.choices[0].message.content}


# -----------------------------------------
# AI — TASK GENERATOR
# -----------------------------------------
@app.post("/generate_task", response_model=TaskDB)
def generate_task_route(body: TaskPrompt, db: Session = Depends(get_db)):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Return ONLY valid JSON. "
                    "NO explanations, NO extra text, NO markdown. "
                    "Format: {\"title\": \"...\", \"description\": \"...\"}"
                )
            },
            {"role": "user", "content": f"Create a task for: {body.prompt}"},
        ],
    )

    text = response.choices[0].message.content.strip()

    # cleanup unwanted wrappers
    text = text.replace("```json", "").replace("```", "").strip()

    # extract JSON if extra text exists
    if "{" in text and "}" in text:
        text = text[text.index("{"): text.rindex("}") + 1]

    try:
        data = json.loads(text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid AI output: {text}"
        )

    new_task = TaskModel(
        title=data.get("title", "Untitled Task"),
        description=data.get("description", "")
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
