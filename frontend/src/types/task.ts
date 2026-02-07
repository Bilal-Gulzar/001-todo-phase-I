export interface Task {
  id: string;  // Changed from number to string to match UUID
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}