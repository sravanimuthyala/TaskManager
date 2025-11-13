
import React, { useState } from 'react';
import { InputGroup, FormControl, Button } from 'react-bootstrap';
import { PlusCircleFill } from 'react-bootstrap-icons';

export default function TaskForm({ onAdd }) {
  const [title, setTitle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (title.trim()) {
      onAdd(title);
      setTitle('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <InputGroup>
        <FormControl
          placeholder="🆕 Add a new task..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="shadow-sm"
        />
        <Button
          variant="primary"
          type="submit"
          className="d-flex align-items-center px-3"
        >
          <PlusCircleFill className="me-2" />
          Add Task
        </Button>
      </InputGroup>
    </form>
  );
}