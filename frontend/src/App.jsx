import React, { useEffect, useState } from 'react';
import {
  getTasks,
  addTask,
  updateTask,
  deleteTask,
  generateTask,
  getRecommendations
} from './api/Api';

import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState("");

  // Load tasks
  const fetchTasks = async () => {
    try {
      const res = await getTasks();
      setTasks(res.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // Add normal task
  const handleAdd = async (title) => {
    try {
      await addTask(title);
      fetchTasks();
    } catch (error) {
      console.error("Error adding task:", error);
    }
  };

  // Update task (edit or toggle)
  const handleUpdate = async (task) => {
    try {
      // If called from checkbox toggle, task already contains updated fields
      await updateTask(task.id, task.title, task.completed);
      fetchTasks();
    } catch (error) {
      console.error("Error updating task:", error);
    }
  };

  // Delete task
  const handleDelete = async (id) => {
    try {
      await deleteTask(id);
      fetchTasks();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  // 🌸 Generate Task using Gemini AI
  const handleGenerateTask = async () => {
    if (!prompt.trim()) return alert("Enter something to generate a task!");

    try {
      await generateTask(prompt);
      setPrompt("");
      fetchTasks();
    } catch (error) {
      console.error("AI generation error:", error);
      alert("Gemini failed to generate task. Check backend console.");
    }
  };

  // 🌸 Get AI Recommendations
  const handleGetRecommendations = async () => {
    try {
      const res = await getRecommendations();
      setAiResponse(res.data.recommendation || "No recommendation available.");
    } catch (error) {
      console.error("Recommendation error:", error);
      alert("Gemini failed to give recommendations.");
    }
  };

  return (
    <div
      className="container-fluid d-flex justify-content-center align-items-center"
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #bfdbfe 0%, #c084fc 100%)",
      }}
    >
      <div
        className="card shadow-lg border-0 rounded-4 w-100"
        style={{
          maxWidth: "600px",
          backgroundColor: "#ffffffd9",
          backdropFilter: "blur(10px)",
        }}
      >
        <div className="card-body p-4">
          <h1 className="text-center mb-4 fw-bold text-primary">📝 Task Manager</h1>

          {/* Manual Task Form */}
          <TaskForm onAdd={handleAdd} />

          {/* Task List */}
          <TaskList
            tasks={tasks}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />

          {/* 🌸 AI Task Generator UI */}
          <div className="mt-4">
            <h5 className="fw-bold">✨ AI Task Generator (Gemini)</h5>

            <div className="input-group mb-3">
              <input
                type="text"
                className="form-control"
                placeholder="Tell Gemini: e.g. 'Plan my study schedule'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
              <button className="btn btn-primary" onClick={handleGenerateTask}>
                Generate
              </button>
            </div>

            <button className="btn btn-info w-100 mb-3" onClick={handleGetRecommendations}>
              Get AI Recommendations 💡
            </button>

            {aiResponse && (
              <div
                className="p-3 rounded bg-light shadow-sm"
                style={{ whiteSpace: "pre-line" }}
              >
                <strong>AI Recommendations:</strong>
                <p>{aiResponse}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
