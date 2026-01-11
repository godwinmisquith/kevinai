import { useState } from 'react';
import {
  CheckCircle2,
  Circle,
  Clock,
  Plus,
  Trash2,
  ListTodo,
} from 'lucide-react';
import type { Todo } from '../types';

interface TodoPanelProps {
  todos: Todo[];
  onUpdateTodos: (todos: Partial<Todo>[]) => void;
}

export function TodoPanel({ todos, onUpdateTodos }: TodoPanelProps) {
  const [newTodoContent, setNewTodoContent] = useState('');

  const getStatusIcon = (status: Todo['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />;
      default:
        return <Circle className="w-4 h-4 text-kevin-muted" />;
    }
  };

  const getStatusStyle = (status: Todo['status']) => {
    switch (status) {
      case 'completed':
        return 'line-through text-kevin-muted';
      case 'in_progress':
        return 'text-yellow-400';
      default:
        return 'text-kevin-text';
    }
  };

  const handleStatusChange = (todoId: string, currentStatus: Todo['status']) => {
    const statusOrder: Todo['status'][] = ['pending', 'in_progress', 'completed'];
    const currentIndex = statusOrder.indexOf(currentStatus);
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];

    const updatedTodos = todos.map((t) =>
      t.id === todoId ? { ...t, status: nextStatus } : t
    );
    onUpdateTodos(updatedTodos);
  };

  const handleAddTodo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodoContent.trim()) return;

    const newTodo: Partial<Todo> = {
      content: newTodoContent.trim(),
      status: 'pending',
    };

    onUpdateTodos([...todos, newTodo]);
    setNewTodoContent('');
  };

  const handleDeleteTodo = (todoId: string) => {
    const updatedTodos = todos.filter((t) => t.id !== todoId);
    onUpdateTodos(updatedTodos);
  };

  const completedCount = todos.filter((t) => t.status === 'completed').length;
  const inProgressCount = todos.filter((t) => t.status === 'in_progress').length;

  return (
    <div className="h-full flex flex-col bg-kevin-surface">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-kevin-primary">
        <div className="flex items-center gap-2">
          <ListTodo className="w-4 h-4 text-kevin-accent" />
          <span className="text-sm font-medium">Tasks</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-kevin-muted">
          <span className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-green-500" />
            {completedCount}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-yellow-500" />
            {inProgressCount}
          </span>
          <span className="flex items-center gap-1">
            <Circle className="w-3 h-3" />
            {todos.length - completedCount - inProgressCount}
          </span>
        </div>
      </div>

      {/* Todo List */}
      <div className="flex-1 overflow-y-auto p-2">
        {todos.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-kevin-muted text-sm">
            <ListTodo className="w-8 h-8 mb-2" />
            <p>No tasks yet</p>
            <p className="text-xs mt-1">Kevin will create tasks as needed</p>
          </div>
        ) : (
          <ul className="space-y-1">
            {todos.map((todo) => (
              <li
                key={todo.id}
                className="flex items-start gap-2 p-2 rounded hover:bg-kevin-primary transition-colors group"
              >
                <button
                  onClick={() => handleStatusChange(todo.id, todo.status)}
                  className="flex-shrink-0 mt-0.5 hover:scale-110 transition-transform"
                  title={`Status: ${todo.status}. Click to change.`}
                >
                  {getStatusIcon(todo.status)}
                </button>
                <span
                  className={`flex-1 text-sm ${getStatusStyle(todo.status)}`}
                >
                  {todo.content}
                </span>
                <button
                  onClick={() => handleDeleteTodo(todo.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-kevin-accent transition-all"
                  title="Delete task"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Add Todo Form */}
      <form
        onSubmit={handleAddTodo}
        className="p-2 border-t border-kevin-primary"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={newTodoContent}
            onChange={(e) => setNewTodoContent(e.target.value)}
            placeholder="Add a task..."
            className="flex-1 bg-kevin-bg border border-kevin-primary rounded px-3 py-1.5 text-sm focus:outline-none focus:border-kevin-accent transition-colors"
          />
          <button
            type="submit"
            disabled={!newTodoContent.trim()}
            className="px-3 py-1.5 bg-kevin-accent text-white rounded hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* Progress Bar */}
      {todos.length > 0 && (
        <div className="px-3 pb-2">
          <div className="h-1 bg-kevin-bg rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-300"
              style={{
                width: `${(completedCount / todos.length) * 100}%`,
              }}
            />
          </div>
          <p className="text-xs text-kevin-muted mt-1 text-center">
            {completedCount} of {todos.length} completed
          </p>
        </div>
      )}
    </div>
  );
}
