import React from 'react';
import { CheckCircleFill, DashCircleFill, TrashFill, PencilFill } from 'react-bootstrap-icons';

export default function TaskList({ tasks, onUpdate, onDelete }) {
  // Toggle task completion
  const handleToggle = (task) => {
    onUpdate({
      ...task,
      completed: !task.completed,
    });
  };

  return (
    <ul className="list-unstyled mx-auto" style={{ maxWidth: "100%" }}>
      {tasks.map((task) => (
        <li
          key={task.id}
          className="d-flex justify-content-between align-items-center mb-3 p-3 shadow rounded-3"
          style={{
            background: task.completed ? "#e6ffe6" : "#fff7e6",
            borderLeft: task.completed ? "6px solid #28a745" : "6px solid #ffc107",
            transition: "0.3s",
          }}
        >
          {/* LEFT SIDE */}
          <div className="d-flex align-items-center">

            {/* Toggle Checkbox */}
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleToggle(task)}
              className="me-3"
              style={{ width: "18px", height: "18px" }}
            />

            <div>
              {/* Task Title */}
              <strong
                style={{
                  textDecoration: task.completed ? "line-through" : "none",
                }}
              >
                {task.title}
              </strong>

              {/* Optional Description (AI-generated) */}
              {task.description && (
                <div
                  style={{
                    fontSize: "0.85rem",
                    color: "#555",
                    marginTop: "4px",
                  }}
                >
                  ➤ {task.description}
                </div>
              )}
            </div>
          </div>

          {/* RIGHT SIDE BUTTONS */}
          <div>
            {/* Edit */}
            <button
              className="btn btn-sm btn-outline-primary me-2"
              onClick={() => onUpdate(task)}
            >
              <PencilFill size={14} className="me-1" />
              Edit
            </button>

            {/* Delete */}
            <button
              className="btn btn-sm btn-outline-danger"
              onClick={() => onDelete(task.id)}
            >
              <TrashFill size={14} className="me-1" />
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
