# Phase 3 Frontend UI Specification: Todo Evolution

## Overview
This specification defines the user interface for the Todo application frontend built with Next.js 15. The UI will connect to the backend API to manage tasks and provide a responsive, accessible user experience.

## UI Components

### 1. Header Component
- **Location**: Top of the page
- **Content**: Displays the text "Todo Evolution"
- **Styling**: Prominent typography, consistent with the overall design system
- **Responsiveness**: Adapts to different screen sizes while maintaining readability

### 2. Task Input Form
- **Location**: Below the header, prominently displayed
- **Component**: Input field with accompanying submit button
- **Functionality**:
  - Accepts task title (required, 1-100 characters)
  - Optional description field (max 500 characters)
  - Submit button to create new task
  - Form validation for required fields
- **User Experience**:
  - Clear placeholder text guiding user input
  - Visual feedback during submission
  - Error handling for validation failures

### 3. Task List Component
- **Location**: Main content area below the input form
- **Functionality**: Displays all tasks retrieved from the backend
- **Features**:
  - Shows task title and description
  - Displays completion status with visual indicators
  - Sorts tasks by creation date (newest first)
  - Responsive grid/list layout depending on screen size

### 4. Individual Task Item
- **Elements**:
  - Checkbox for marking task as complete/incomplete
  - Task title (displayed with strikethrough when completed)
  - Task description (optional, shown below title)
  - Delete button with confirmation
- **Interactions**:
  - Clicking checkbox updates completion status via API
  - Delete button removes task from list and backend
  - Hover effects for better UX

## API Integration

### 1. Backend Connection
- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP with JSON payload
- **Authentication**: None required (public API for Phase 2)

### 2. API Endpoints Used
- **GET** `/tasks` - Retrieve all tasks
  - Method: GET
  - Response: Array of task objects
  - Error handling: Display error message if fetch fails
- **POST** `/tasks` - Create a new task
  - Method: POST
  - Request body: `{ "title": "task title", "description": "optional description" }`
  - Response: Created task object
  - Error handling: Display validation errors
- **PATCH** `/tasks/{id}` - Update task status
  - Method: PATCH
  - Request body: `{ "is_completed": true/false }`
  - Response: Updated task object
  - Error handling: Revert UI state if update fails
- **DELETE** `/tasks/{id}` - Delete a task
  - Method: DELETE
  - Response: 204 No Content
  - Error handling: Show error message if deletion fails

### 3. Data Fetching Strategy
- **Option 1**: Native `fetch` API with React state management
- **Option 2**: TanStack Query (React Query) for advanced caching, background updates, and optimistic updates
- **Recommendation**: TanStack Query for better user experience with loading states, error handling, and offline support

## User Experience Features

### 1. Loading States
- Visual indicators when data is being fetched
- Skeleton loaders for task list during initial load
- Optimistic updates for immediate UI feedback

### 2. Error Handling
- Network error notifications
- Validation error display
- Retry mechanisms for failed requests

### 3. Responsive Design
- Mobile-first approach
- Adapts to various screen sizes (mobile, tablet, desktop)
- Touch-friendly controls for mobile devices

## Technical Implementation

### 1. Component Hierarchy
```
App
├── Header
├── TaskInputForm
├── TaskList
│   └── TaskItem (repeated for each task)
└── Footer (optional)
```

### 2. State Management
- Local component state for form inputs
- Global state (or TanStack Query cache) for task data
- Loading and error states for API interactions

### 3. Styling
- Tailwind CSS for utility-first styling
- Responsive design with breakpoints
- Dark/light mode support leveraging existing Next.js setup

## Accessibility Requirements
- Keyboard navigation support
- Screen reader compatibility
- Sufficient color contrast
- Semantic HTML elements
- ARIA labels where necessary

## Performance Considerations
- Efficient rendering of task list (virtualization if needed for large datasets)
- Debounced input for search/filtering
- Optimistic updates for better perceived performance
- Proper cleanup of side effects

## Testing Requirements
- Unit tests for individual components
- Integration tests for API interactions
- Accessibility testing
- Responsive design verification