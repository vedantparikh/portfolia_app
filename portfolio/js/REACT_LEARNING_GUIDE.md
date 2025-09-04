# React Learning Guide for Beginners

## Table of Contents

1. [What is React?](#what-is-react)
2. [Setting Up Your Development Environment](#setting-up-your-development-environment)
3. [Understanding JSX](#understanding-jsx)
4. [Components - The Building Blocks](#components---the-building-blocks)
5. [Props - Passing Data Between Components](#props---passing-data-between-components)
6. [State - Making Components Interactive](#state---making-components-interactive)
7. [Event Handling](#event-handling)
8. [Conditional Rendering](#conditional-rendering)
9. [Lists and Keys](#lists-and-keys)
10. [Forms and Controlled Components](#forms-and-controlled-components)
11. [Hooks - Modern React](#hooks---modern-react)
12. [Context API - Sharing Data](#context-api---sharing-data)
13. [Routing - Navigation Between Pages](#routing---navigation-between-pages)
14. [API Integration](#api-integration)
15. [Styling in React](#styling-in-react)
16. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
17. [Debugging React Applications](#debugging-react-applications)
18. [Next Steps](#next-steps)

## What is React?

React is a JavaScript library for building user interfaces, particularly web applications. Think of it as a way to create interactive websites by breaking them down into small, reusable pieces called **components**.

### Why React?

- **Component-Based**: Build complex UIs from simple, reusable pieces
- **Declarative**: Describe what you want, React figures out how to do it
- **Efficient**: Only updates parts of the page that actually changed
- **Popular**: Huge community and job market
- **Flexible**: Can be used for web, mobile, and desktop apps

### Key Concepts

- **Components**: Reusable pieces of UI (like LEGO blocks)
- **JSX**: A syntax that lets you write HTML-like code in JavaScript
- **State**: Data that can change and causes the UI to update
- **Props**: Data passed from parent to child components

## Setting Up Your Development Environment

### Prerequisites

- **Node.js**: Download from [nodejs.org](https://nodejs.org/)
- **Code Editor**: VS Code recommended
- **Browser**: Chrome or Firefox with developer tools

### Creating a React App

```bash
# Create a new React app
npx create-react-app my-first-app

# Navigate to the project
cd my-first-app

# Start the development server
npm start
```

### Project Structure

```
my-first-app/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Understanding JSX

JSX (JavaScript XML) is a syntax extension that lets you write HTML-like code in JavaScript.

### Basic JSX

```javascript
// This is JSX
const element = <h1>Hello, World!</h1>;

// It gets compiled to this JavaScript
const element = React.createElement("h1", null, "Hello, World!");
```

### JSX Rules

1. **One Parent Element**: JSX must have one parent element

```javascript
// ❌ Wrong - multiple parent elements
return (
  <h1>Title</h1>
  <p>Paragraph</p>
);

// ✅ Correct - wrapped in one parent
return (
  <div>
    <h1>Title</h1>
    <p>Paragraph</p>
  </div>
);
```

2. **Self-Closing Tags**: All tags must be closed

```javascript
// ❌ Wrong
<img src="image.jpg">

// ✅ Correct
<img src="image.jpg" />
```

3. **JavaScript in JSX**: Use curly braces `{}`

```javascript
const name = "John";
const element = <h1>Hello, {name}!</h1>;
```

4. **className instead of class**

```javascript
// ❌ Wrong
<div class="container">

// ✅ Correct
<div className="container">
```

## Components - The Building Blocks

Components are the heart of React. They are reusable pieces of UI that can contain both structure and behavior.

### Function Components

```javascript
// Simple function component
function Welcome() {
  return <h1>Hello, World!</h1>;
}

// Arrow function component
const Welcome = () => {
  return <h1>Hello, World!</h1>;
};

// Using the component
function App() {
  return (
    <div>
      <Welcome />
      <Welcome />
      <Welcome />
    </div>
  );
}
```

### Class Components (Legacy)

```javascript
class Welcome extends React.Component {
  render() {
    return <h1>Hello, World!</h1>;
  }
}
```

### Component Composition

```javascript
// Small, focused components
function Header() {
  return <header>My App</header>;
}

function Main() {
  return <main>Main content</main>;
}

function Footer() {
  return <footer>Footer content</footer>;
}

// Compose them together
function App() {
  return (
    <div>
      <Header />
      <Main />
      <Footer />
    </div>
  );
}
```

## Props - Passing Data Between Components

Props (properties) are how you pass data from parent to child components.

### Basic Props

```javascript
// Parent component
function App() {
  return <Welcome name="John" age={25} />;
}

// Child component
function Welcome(props) {
  return (
    <div>
      <h1>Hello, {props.name}!</h1>
      <p>You are {props.age} years old.</p>
    </div>
  );
}
```

### Destructuring Props

```javascript
// More readable way
function Welcome({ name, age }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>You are {age} years old.</p>
    </div>
  );
}
```

### Default Props

```javascript
function Welcome({ name = "Guest", age = 0 }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>You are {age} years old.</p>
    </div>
  );
}
```

### Props with Objects

```javascript
// Parent
const user = { name: "John", age: 25, city: "New York" };
<Welcome user={user} />;

// Child
function Welcome({ user }) {
  return (
    <div>
      <h1>Hello, {user.name}!</h1>
      <p>You are {user.age} years old.</p>
      <p>You live in {user.city}.</p>
    </div>
  );
}
```

## State - Making Components Interactive

State is data that can change over time. When state changes, React re-renders the component.

### useState Hook

```javascript
import React, { useState } from "react";

function Counter() {
  // Declare state variable
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>Click me</button>
    </div>
  );
}
```

### Multiple State Variables

```javascript
function Form() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [age, setAge] = useState(0);

  return (
    <form>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
      />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="number"
        value={age}
        onChange={(e) => setAge(Number(e.target.value))}
        placeholder="Age"
      />
    </form>
  );
}
```

### State with Objects

```javascript
function UserProfile() {
  const [user, setUser] = useState({
    name: "",
    email: "",
    age: 0,
  });

  const updateUser = (field, value) => {
    setUser((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  return (
    <div>
      <input
        value={user.name}
        onChange={(e) => updateUser("name", e.target.value)}
        placeholder="Name"
      />
      <input
        value={user.email}
        onChange={(e) => updateUser("email", e.target.value)}
        placeholder="Email"
      />
    </div>
  );
}
```

## Event Handling

React uses synthetic events that work the same across all browsers.

### Basic Event Handling

```javascript
function Button() {
  const handleClick = () => {
    alert("Button clicked!");
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Event with Parameters

```javascript
function TodoList() {
  const [todos, setTodos] = useState(["Learn React", "Build app"]);

  const handleDelete = (index) => {
    setTodos(todos.filter((_, i) => i !== index));
  };

  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          {todo}
          <button onClick={() => handleDelete(index)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

### Form Events

```javascript
function ContactForm() {
  const [formData, setFormData] = useState({ name: "", email: "" });

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page refresh
    console.log("Form submitted:", formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Name"
      />
      <input
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Conditional Rendering

Show different content based on conditions.

### if/else Statements

```javascript
function Greeting({ isLoggedIn }) {
  if (isLoggedIn) {
    return <h1>Welcome back!</h1>;
  } else {
    return <h1>Please log in.</h1>;
  }
}
```

### Ternary Operator

```javascript
function Greeting({ isLoggedIn }) {
  return (
    <div>{isLoggedIn ? <h1>Welcome back!</h1> : <h1>Please log in.</h1>}</div>
  );
}
```

### Logical && Operator

```javascript
function Mailbox({ unreadMessages }) {
  return (
    <div>
      <h1>Hello!</h1>
      {unreadMessages.length > 0 && (
        <h2>You have {unreadMessages.length} unread messages.</h2>
      )}
    </div>
  );
}
```

### Multiple Conditions

```javascript
function Status({ status }) {
  return (
    <div>
      {status === "loading" && <p>Loading...</p>}
      {status === "success" && <p>Success!</p>}
      {status === "error" && <p>Error occurred!</p>}
    </div>
  );
}
```

## Lists and Keys

Render lists of items efficiently.

### Basic List

```javascript
function TodoList() {
  const todos = ["Learn React", "Build app", "Deploy app"];

  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>{todo}</li>
      ))}
    </ul>
  );
}
```

### List with Objects

```javascript
function UserList() {
  const users = [
    { id: 1, name: "John", age: 25 },
    { id: 2, name: "Jane", age: 30 },
    { id: 3, name: "Bob", age: 35 },
  ];

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.name} is {user.age} years old
        </li>
      ))}
    </ul>
  );
}
```

### Why Keys Matter

Keys help React identify which items have changed, been added, or removed. They should be unique and stable.

```javascript
// ❌ Bad - using index as key when list can change
{
  todos.map((todo, index) => <li key={index}>{todo}</li>);
}

// ✅ Good - using unique ID
{
  todos.map((todo) => <li key={todo.id}>{todo.text}</li>);
}
```

## Forms and Controlled Components

React forms are "controlled" - the form data is handled by React state.

### Controlled Input

```javascript
function NameForm() {
  const [name, setName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Hello, " + name + "!");
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Name:
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Multiple Form Fields

```javascript
function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form data:", formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Name"
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
        placeholder="Message"
      />
      <button type="submit">Send</button>
    </form>
  );
}
```

### Form Validation

```javascript
function LoginForm() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      console.log("Form is valid!");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          name="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          placeholder="Email"
        />
        {errors.email && <span style={{ color: "red" }}>{errors.email}</span>}
      </div>
      <div>
        <input
          name="password"
          type="password"
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          placeholder="Password"
        />
        {errors.password && (
          <span style={{ color: "red" }}>{errors.password}</span>
        )}
      </div>
      <button type="submit">Login</button>
    </form>
  );
}
```

## Hooks - Modern React

Hooks let you use state and other React features in function components.

### useState Hook

```javascript
import React, { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
    </div>
  );
}
```

### useEffect Hook

Runs code after render, like componentDidMount and componentDidUpdate.

```javascript
import React, { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // This runs after every render
    fetchUser(userId);
  }, [userId]); // Only run when userId changes

  const fetchUser = async (id) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/users/${id}`);
      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error("Error fetching user:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### useEffect Cleanup

```javascript
function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    // Cleanup function
    return () => clearInterval(interval);
  }, []); // Empty dependency array means run once

  return <div>Timer: {seconds} seconds</div>;
}
```

### Custom Hooks

Create your own hooks to reuse stateful logic.

```javascript
// Custom hook
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(initialValue);

  return { count, increment, decrement, reset };
}

// Using the custom hook
function Counter() {
  const { count, increment, decrement, reset } = useCounter(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

## Context API - Sharing Data

Context provides a way to share data between components without passing props down manually.

### Creating Context

```javascript
import React, { createContext, useContext, useState } from "react";

// Create context
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to use context
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}

// Using the context
function App() {
  return (
    <ThemeProvider>
      <Header />
      <Main />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header style={{ background: theme === "light" ? "#fff" : "#333" }}>
      <h1>My App</h1>
      <button onClick={toggleTheme}>
        Switch to {theme === "light" ? "dark" : "light"} theme
      </button>
    </header>
  );
}
```

## Routing - Navigation Between Pages

React Router enables client-side routing.

### Basic Setup

```bash
npm install react-router-dom
```

```javascript
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </BrowserRouter>
  );
}

function Home() {
  return <h1>Home Page</h1>;
}

function About() {
  return <h1>About Page</h1>;
}

function Contact() {
  return <h1>Contact Page</h1>;
}
```

### Navigation with useNavigate

```javascript
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: "", password: "" });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate login
    if (formData.email && formData.password) {
      navigate("/dashboard"); // Navigate to dashboard
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
      />
      <input
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## API Integration

Making HTTP requests to fetch and send data.

### Fetch API

```javascript
import { useState, useEffect } from "react";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/users");
      if (!response.ok) {
        throw new Error("Failed to fetch users");
      }
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Axios (Recommended)

```bash
npm install axios
```

```javascript
import axios from "axios";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get("/api/users");
        setUsers(response.data);
      } catch (error) {
        console.error("Error fetching users:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### POST Request

```javascript
function CreateUser() {
  const [formData, setFormData] = useState({ name: "", email: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("/api/users", formData);
      console.log("User created:", response.data);
      // Reset form
      setFormData({ name: "", email: "" });
    } catch (error) {
      console.error("Error creating user:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Name"
      />
      <input
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
      />
      <button type="submit">Create User</button>
    </form>
  );
}
```

## Styling in React

### CSS Classes

```javascript
// In your CSS file
.button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
}

// In your component
function Button() {
  return <button className="button">Click me</button>;
}
```

### Inline Styles

```javascript
function Button() {
  const buttonStyle = {
    backgroundColor: "blue",
    color: "white",
    padding: "10px 20px",
    border: "none",
    borderRadius: "4px",
  };

  return <button style={buttonStyle}>Click me</button>;
}
```

### CSS Modules

```javascript
// Button.module.css
.button {
  background-color: blue;
  color: white;
}

// Button.js
import styles from './Button.module.css';

function Button() {
  return <button className={styles.button}>Click me</button>;
}
```

### Styled Components

```bash
npm install styled-components
```

```javascript
import styled from "styled-components";

const StyledButton = styled.button`
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;

  &:hover {
    background-color: darkblue;
  }
`;

function Button() {
  return <StyledButton>Click me</StyledButton>;
}
```

## Common Patterns and Best Practices

### 1. Component Composition

```javascript
// Instead of one large component
function UserProfile({ user }) {
  return (
    <div>
      <UserHeader user={user} />
      <UserDetails user={user} />
      <UserActions user={user} />
    </div>
  );
}
```

### 2. Lifting State Up

```javascript
// Move shared state to common parent
function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <Display count={count} />
      <Controls count={count} setCount={setCount} />
    </div>
  );
}
```

### 3. Controlled vs Uncontrolled Components

```javascript
// Controlled - React controls the value
function ControlledInput() {
  const [value, setValue] = useState("");
  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
}

// Uncontrolled - DOM controls the value
function UncontrolledInput() {
  return <input defaultValue="initial value" />;
}
```

### 4. Key Props

```javascript
// Always use stable, unique keys
{
  todos.map((todo) => <TodoItem key={todo.id} todo={todo} />);
}
```

### 5. Conditional Rendering

```javascript
// Use early returns for cleaner code
function UserProfile({ user }) {
  if (!user) return <div>Loading...</div>;
  if (user.error) return <div>Error: {user.error}</div>;

  return <div>{user.name}</div>;
}
```

## Debugging React Applications

### 1. React Developer Tools

Install the React Developer Tools browser extension for Chrome or Firefox.

### 2. Console Logging

```javascript
function MyComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    console.log("Component mounted");
    return () => console.log("Component unmounted");
  }, []);

  console.log("Rendering with data:", data);

  return <div>My Component</div>;
}
```

### 3. Error Boundaries

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}
```

### 4. Common Debugging Tips

- Check the browser console for errors
- Use React DevTools to inspect component state
- Add console.log statements to track data flow
- Use the Network tab to check API requests
- Verify props are being passed correctly

## Next Steps

### 1. Build Projects

- Todo app with local storage
- Weather app with API
- Blog with routing
- E-commerce site with state management

### 2. Learn Advanced Topics

- Performance optimization
- Testing (Jest, React Testing Library)
- State management (Redux, Zustand)
- Server-side rendering (Next.js)
- Mobile development (React Native)

### 3. Resources

- [React Official Documentation](https://react.dev/)
- [React Tutorial](https://react.dev/learn)
- [React Patterns](https://reactpatterns.com/)
- [React Hooks Guide](https://react.dev/reference/react)

### 4. Practice Exercises

1. Create a counter with increment/decrement buttons
2. Build a todo list with add/remove functionality
3. Make a weather app that fetches data from an API
4. Create a simple blog with routing between pages
5. Build a form with validation

Remember: The best way to learn React is by building projects and experimenting with the code. Don't be afraid to make mistakes - that's how you learn!
