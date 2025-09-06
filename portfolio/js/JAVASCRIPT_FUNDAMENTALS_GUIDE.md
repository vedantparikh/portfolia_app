# JavaScript Fundamentals Guide for React Beginners

## Table of Contents

1. [What is JavaScript?](#what-is-javascript)
2. [Variables and Data Types](#variables-and-data-types)
3. [Functions](#functions)
4. [Objects and Arrays](#objects-and-arrays)
5. [Destructuring](#destructuring)
6. [Template Literals](#template-literals)
7. [Arrow Functions](#arrow-functions)
8. [Promises and Async/Await](#promises-and-asyncawait)
9. [Modules (Import/Export)](#modules-importexport)
10. [Array Methods](#array-methods)
11. [Object Methods](#object-methods)
12. [Spread and Rest Operators](#spread-and-rest-operators)
13. [Conditional Logic](#conditional-logic)
14. [Loops](#loops)
15. [Error Handling](#error-handling)
16. [Common Patterns in React](#common-patterns-in-react)
17. [Practice Exercises](#practice-exercises)

## What is JavaScript?

JavaScript is a programming language that makes websites interactive. It runs in your browser and can:

- Change HTML content
- Respond to user actions (clicks, form submissions)
- Make requests to servers
- Store and manipulate data
- Create animations and effects

### Why Learn JavaScript for React?

React is built with JavaScript, so understanding JavaScript fundamentals is essential for:

- Writing React components
- Managing state and props
- Handling events
- Making API calls
- Understanding React's syntax and patterns

## Variables and Data Types

### Declaring Variables

```javascript
// Three ways to declare variables
var name = "John"; // Old way, avoid in modern code
let age = 25; // Can be reassigned
const city = "New York"; // Cannot be reassigned

// Use const by default, let when you need to reassign
const isStudent = true;
let currentYear = 2024;
```

### Data Types

```javascript
// Primitive types
const string = "Hello World";           // Text
const number = 42;                      // Numbers
const boolean = true;                   // true or false
const undefined = undefined;            // Not defined
const null = null;                      // Intentionally empty
const symbol = Symbol('id');            // Unique identifier

// Object types
const object = { name: "John", age: 25 };
const array = [1, 2, 3, 4, 5];
const function = () => console.log("Hello");

// Check data type
console.log(typeof string);    // "string"
console.log(typeof number);    // "number"
console.log(typeof boolean);   // "boolean"
console.log(typeof object);    // "object"
console.log(typeof array);     // "object" (arrays are objects)
console.log(typeof function);  // "function"
```

### Type Coercion

```javascript
// JavaScript automatically converts types
console.log("5" + 3); // "53" (string concatenation)
console.log("5" - 3); // 2 (number subtraction)
console.log("5" * 3); // 15 (number multiplication)
console.log("5" / 3); // 1.666... (number division)

// Explicit conversion
console.log(Number("5")); // 5
console.log(String(5)); // "5"
console.log(Boolean(1)); // true
console.log(Boolean(0)); // false
```

## Functions

### Function Declarations

```javascript
// Basic function
function greet(name) {
  return "Hello, " + name + "!";
}

console.log(greet("John")); // "Hello, John!"

// Function with multiple parameters
function add(a, b) {
  return a + b;
}

console.log(add(5, 3)); // 8
```

### Function Expressions

```javascript
// Assigning function to variable
const multiply = function (a, b) {
  return a * b;
};

console.log(multiply(4, 5)); // 20
```

### Arrow Functions (ES6+)

```javascript
// Arrow function syntax
const divide = (a, b) => {
  return a / b;
};

// Shorter syntax for single expression
const square = (x) => x * x;

// No parameters
const sayHello = () => "Hello!";

// Multiple parameters
const fullName = (firstName, lastName) => firstName + " " + lastName;

console.log(divide(10, 2)); // 5
console.log(square(4)); // 16
console.log(sayHello()); // "Hello!"
console.log(fullName("John", "Doe")); // "John Doe"
```

### Default Parameters

```javascript
function greet(name = "Guest") {
  return "Hello, " + name + "!";
}

console.log(greet()); // "Hello, Guest!"
console.log(greet("Alice")); // "Hello, Alice!"
```

### Higher-Order Functions

```javascript
// Function that takes another function as parameter
function processArray(array, processor) {
  const result = [];
  for (let item of array) {
    result.push(processor(item));
  }
  return result;
}

const numbers = [1, 2, 3, 4, 5];
const doubled = processArray(numbers, (x) => x * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// Function that returns another function
function createMultiplier(factor) {
  return function (number) {
    return number * factor;
  };
}

const double = createMultiplier(2);
const triple = createMultiplier(3);

console.log(double(5)); // 10
console.log(triple(5)); // 15
```

## Objects and Arrays

### Objects

```javascript
// Creating objects
const person = {
  name: "John",
  age: 25,
  city: "New York",
  isStudent: true,
};

// Accessing properties
console.log(person.name); // "John"
console.log(person["age"]); // 25

// Adding properties
person.email = "john@example.com";
person["phone"] = "123-456-7890";

// Nested objects
const user = {
  name: "Alice",
  address: {
    street: "123 Main St",
    city: "Boston",
    zipCode: "02101",
  },
  hobbies: ["reading", "cooking", "hiking"],
};

console.log(user.address.city); // "Boston"
console.log(user.hobbies[0]); // "reading"
```

### Arrays

```javascript
// Creating arrays
const fruits = ["apple", "banana", "orange"];
const numbers = [1, 2, 3, 4, 5];
const mixed = ["hello", 42, true, { name: "John" }];

// Accessing elements
console.log(fruits[0]); // "apple"
console.log(fruits[1]); // "banana"
console.log(fruits.length); // 3

// Adding elements
fruits.push("grape"); // Add to end
fruits.unshift("kiwi"); // Add to beginning

// Removing elements
fruits.pop(); // Remove from end
fruits.shift(); // Remove from beginning

console.log(fruits); // ["banana", "orange", "grape"]
```

### Array Methods

```javascript
const numbers = [1, 2, 3, 4, 5];

// forEach - execute function for each element
numbers.forEach((num) => console.log(num * 2));

// map - create new array with transformed elements
const doubled = numbers.map((num) => num * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// filter - create new array with elements that pass test
const evenNumbers = numbers.filter((num) => num % 2 === 0);
console.log(evenNumbers); // [2, 4]

// find - find first element that passes test
const found = numbers.find((num) => num > 3);
console.log(found); // 4

// reduce - reduce array to single value
const sum = numbers.reduce((total, num) => total + num, 0);
console.log(sum); // 15

// some - check if any element passes test
const hasEven = numbers.some((num) => num % 2 === 0);
console.log(hasEven); // true

// every - check if all elements pass test
const allPositive = numbers.every((num) => num > 0);
console.log(allPositive); // true
```

## Destructuring

### Object Destructuring

```javascript
const person = {
  name: "John",
  age: 25,
  city: "New York",
  email: "john@example.com",
};

// Basic destructuring
const { name, age } = person;
console.log(name); // "John"
console.log(age); // 25

// Destructuring with different variable names
const { name: fullName, age: years } = person;
console.log(fullName); // "John"
console.log(years); // 25

// Destructuring with default values
const { name, age, country = "USA" } = person;
console.log(country); // "USA"

// Nested destructuring
const user = {
  name: "Alice",
  address: {
    street: "123 Main St",
    city: "Boston",
  },
};

const {
  address: { city },
} = user;
console.log(city); // "Boston"
```

### Array Destructuring

```javascript
const colors = ["red", "green", "blue"];

// Basic destructuring
const [first, second, third] = colors;
console.log(first); // "red"
console.log(second); // "green"
console.log(third); // "blue"

// Skip elements
const [first, , third] = colors;
console.log(first); // "red"
console.log(third); // "blue"

// Rest operator
const [first, ...rest] = colors;
console.log(first); // "red"
console.log(rest); // ["green", "blue"]

// Default values
const [a, b, c, d = "yellow"] = colors;
console.log(d); // "yellow"
```

## Template Literals

Template literals use backticks (`) and allow for:

- Multi-line strings
- Variable interpolation
- Expression evaluation

```javascript
const name = "John";
const age = 25;
const city = "New York";

// Basic template literal
const message = `Hello, my name is ${name} and I am ${age} years old.`;
console.log(message);
// "Hello, my name is John and I am 25 years old."

// Multi-line strings
const multiLine = `
  This is a
  multi-line
  string.
`;

// Expressions in template literals
const calculation = `The sum of 5 and 3 is ${5 + 3}.`;
console.log(calculation); // "The sum of 5 and 3 is 8."

// Function calls in template literals
const greet = (name) => `Hello, ${name}!`;
const greeting = `Welcome! ${greet("Alice")}`;
console.log(greeting); // "Welcome! Hello, Alice!"
```

## Arrow Functions

Arrow functions are a shorter syntax for writing functions.

```javascript
// Traditional function
function add(a, b) {
  return a + b;
}

// Arrow function
const add = (a, b) => {
  return a + b;
};

// Arrow function with single expression (implicit return)
const add = (a, b) => a + b;

// Single parameter (parentheses optional)
const square = (x) => x * x;

// No parameters
const greet = () => "Hello!";

// Multiple parameters
const fullName = (firstName, lastName) => `${firstName} ${lastName}`;

// Returning object (need parentheses)
const createUser = (name, age) => ({ name, age });

// Arrow functions in array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((num) => num * 2);
const evens = numbers.filter((num) => num % 2 === 0);
const sum = numbers.reduce((total, num) => total + num, 0);
```

### Arrow Functions vs Regular Functions

```javascript
// 'this' binding is different
const obj = {
  name: "John",
  regularFunction: function () {
    console.log(this.name); // "John" (this refers to obj)
  },
  arrowFunction: () => {
    console.log(this.name); // undefined (this refers to global scope)
  },
};

obj.regularFunction(); // "John"
obj.arrowFunction(); // undefined

// Arrow functions don't have their own 'this'
// They inherit 'this' from the surrounding scope
```

## Promises and Async/Await

### Promises

Promises represent the eventual completion of an asynchronous operation.

```javascript
// Creating a promise
const fetchData = () => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;
      if (success) {
        resolve("Data fetched successfully!");
      } else {
        reject("Failed to fetch data");
      }
    }, 1000);
  });
};

// Using promises
fetchData()
  .then((data) => {
    console.log(data);
  })
  .catch((error) => {
    console.error(error);
  })
  .finally(() => {
    console.log("Operation completed");
  });
```

### Async/Await

Async/await is a cleaner way to work with promises.

```javascript
// Async function
const fetchDataAsync = async () => {
  try {
    const data = await fetchData();
    console.log(data);
  } catch (error) {
    console.error(error);
  } finally {
    console.log("Operation completed");
  }
};

// Using async/await
fetchDataAsync();
```

### Real-world Example with Fetch

```javascript
// Fetching data from an API
const fetchUser = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch user");
    }
    const user = await response.json();
    return user;
  } catch (error) {
    console.error("Error fetching user:", error);
    throw error;
  }
};

// Using the function
const loadUser = async () => {
  try {
    const user = await fetchUser(123);
    console.log("User loaded:", user);
  } catch (error) {
    console.error("Failed to load user:", error);
  }
};
```

## Modules (Import/Export)

### Exporting

```javascript
// Named exports
export const name = "John";
export const age = 25;
export function greet(name) {
  return `Hello, ${name}!`;
}

// Default export
const User = {
  name: "John",
  age: 25,
};
export default User;

// Exporting multiple items
export { name, age, greet };
```

### Importing

```javascript
// Named imports
import { name, age, greet } from "./user.js";

// Default import
import User from "./user.js";

// Import everything
import * as userModule from "./user.js";

// Renaming imports
import { name as userName, age as userAge } from "./user.js";

// Mixed imports
import User, { greet } from "./user.js";
```

### CommonJS (Node.js style)

```javascript
// Exporting
module.exports = {
  name: "John",
  age: 25,
  greet: function (name) {
    return `Hello, ${name}!`;
  },
};

// Importing
const { name, age, greet } = require("./user.js");
```

## Array Methods

### Essential Array Methods for React

```javascript
const users = [
  { id: 1, name: "John", age: 25, active: true },
  { id: 2, name: "Jane", age: 30, active: false },
  { id: 3, name: "Bob", age: 35, active: true },
];

// map - Transform each element
const userNames = users.map((user) => user.name);
console.log(userNames); // ["John", "Jane", "Bob"]

// filter - Keep elements that pass test
const activeUsers = users.filter((user) => user.active);
console.log(activeUsers); // [{ id: 1, name: "John", age: 25, active: true }, ...]

// find - Find first element that passes test
const user = users.find((user) => user.id === 2);
console.log(user); // { id: 2, name: "Jane", age: 30, active: false }

// some - Check if any element passes test
const hasActiveUsers = users.some((user) => user.active);
console.log(hasActiveUsers); // true

// every - Check if all elements pass test
const allAdults = users.every((user) => user.age >= 18);
console.log(allAdults); // true

// reduce - Reduce array to single value
const totalAge = users.reduce((sum, user) => sum + user.age, 0);
console.log(totalAge); // 90

// forEach - Execute function for each element
users.forEach((user) => {
  console.log(`${user.name} is ${user.age} years old`);
});
```

### Array Methods for State Updates in React

```javascript
// Adding item to array
const addUser = (users, newUser) => {
  return [...users, newUser]; // Spread operator
};

// Removing item from array
const removeUser = (users, userId) => {
  return users.filter((user) => user.id !== userId);
};

// Updating item in array
const updateUser = (users, userId, updates) => {
  return users.map((user) =>
    user.id === userId ? { ...user, ...updates } : user
  );
};

// Toggling boolean property
const toggleUserActive = (users, userId) => {
  return users.map((user) =>
    user.id === userId ? { ...user, active: !user.active } : user
  );
};
```

## Object Methods

### Object.keys(), Object.values(), Object.entries()

```javascript
const person = {
  name: "John",
  age: 25,
  city: "New York",
};

// Get all keys
const keys = Object.keys(person);
console.log(keys); // ["name", "age", "city"]

// Get all values
const values = Object.values(person);
console.log(values); // ["John", 25, "New York"]

// Get key-value pairs
const entries = Object.entries(person);
console.log(entries); // [["name", "John"], ["age", 25], ["city", "New York"]]

// Iterate over object
Object.entries(person).forEach(([key, value]) => {
  console.log(`${key}: ${value}`);
});
```

### Object.assign() and Spread Operator

```javascript
const user = {
  name: "John",
  age: 25,
};

// Object.assign - merge objects
const updatedUser = Object.assign({}, user, { city: "New York" });
console.log(updatedUser); // { name: "John", age: 25, city: "New York" }

// Spread operator - modern way
const updatedUser2 = { ...user, city: "New York" };
console.log(updatedUser2); // { name: "John", age: 25, city: "New York" }

// Deep merge (be careful with nested objects)
const userWithAddress = {
  ...user,
  address: {
    street: "123 Main St",
    city: "Boston",
  },
};
```

## Spread and Rest Operators

### Spread Operator (...)

```javascript
// Arrays
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];
console.log(combined); // [1, 2, 3, 4, 5, 6]

// Objects
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = { ...obj1, ...obj2 };
console.log(merged); // { a: 1, b: 2, c: 3, d: 4 }

// Function arguments
const numbers = [1, 2, 3, 4, 5];
const max = Math.max(...numbers);
console.log(max); // 5

// Copying arrays and objects
const originalArray = [1, 2, 3];
const copiedArray = [...originalArray];

const originalObject = { a: 1, b: 2 };
const copiedObject = { ...originalObject };
```

### Rest Operator (...)

```javascript
// Function parameters
const sum = (...numbers) => {
  return numbers.reduce((total, num) => total + num, 0);
};

console.log(sum(1, 2, 3, 4, 5)); // 15

// Destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];
console.log(first); // 1
console.log(second); // 2
console.log(rest); // [3, 4, 5]

const { name, ...otherProps } = { name: "John", age: 25, city: "NYC" };
console.log(name); // "John"
console.log(otherProps); // { age: 25, city: "NYC" }
```

## Conditional Logic

### if/else Statements

```javascript
const age = 18;

if (age >= 18) {
  console.log("You are an adult");
} else if (age >= 13) {
  console.log("You are a teenager");
} else {
  console.log("You are a child");
}
```

### Ternary Operator

```javascript
const age = 18;
const status = age >= 18 ? "adult" : "minor";
console.log(status); // "adult"

// Nested ternary (use sparingly)
const message = age >= 18 ? "adult" : age >= 13 ? "teenager" : "child";
console.log(message); // "adult"
```

### Logical Operators

```javascript
const user = {
  name: "John",
  age: 25,
  isActive: true,
};

// AND operator (&&)
if (user.name && user.age) {
  console.log("User has name and age");
}

// OR operator (||)
const displayName = user.name || "Anonymous";
console.log(displayName); // "John"

// NOT operator (!)
if (!user.isActive) {
  console.log("User is not active");
}

// Nullish coalescing (??) - only for null/undefined
const count = user.count ?? 0;
console.log(count); // 0
```

### Switch Statements

```javascript
const day = "Monday";

switch (day) {
  case "Monday":
    console.log("Start of work week");
    break;
  case "Friday":
    console.log("End of work week");
    break;
  case "Saturday":
  case "Sunday":
    console.log("Weekend");
    break;
  default:
    console.log("Regular day");
}
```

## Loops

### for Loop

```javascript
const numbers = [1, 2, 3, 4, 5];

// Traditional for loop
for (let i = 0; i < numbers.length; i++) {
  console.log(numbers[i]);
}

// for...of loop (for arrays)
for (const number of numbers) {
  console.log(number);
}

// for...in loop (for objects)
const person = { name: "John", age: 25, city: "NYC" };
for (const key in person) {
  console.log(`${key}: ${person[key]}`);
}
```

### while and do-while

```javascript
let count = 0;

// while loop
while (count < 5) {
  console.log(count);
  count++;
}

// do-while loop (executes at least once)
let i = 0;
do {
  console.log(i);
  i++;
} while (i < 5);
```

### Loop Control

```javascript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// break - exit loop completely
for (const num of numbers) {
  if (num === 5) {
    break; // Stop at 5
  }
  console.log(num); // 1, 2, 3, 4
}

// continue - skip current iteration
for (const num of numbers) {
  if (num % 2 === 0) {
    continue; // Skip even numbers
  }
  console.log(num); // 1, 3, 5, 7, 9
}
```

## Error Handling

### try/catch/finally

```javascript
const divide = (a, b) => {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
};

try {
  const result = divide(10, 0);
  console.log(result);
} catch (error) {
  console.error("Error:", error.message);
} finally {
  console.log("Operation completed");
}
```

### Custom Errors

```javascript
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

const validateUser = (user) => {
  if (!user.name) {
    throw new ValidationError("Name is required", "name");
  }
  if (!user.email) {
    throw new ValidationError("Email is required", "email");
  }
  return true;
};

try {
  validateUser({ name: "John" });
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`Validation error in ${error.field}: ${error.message}`);
  } else {
    console.error("Unexpected error:", error.message);
  }
}
```

## Common Patterns in React

### 1. State Updates

```javascript
// Updating state with objects
const [user, setUser] = useState({ name: "", email: "" });

const updateUser = (field, value) => {
  setUser((prevUser) => ({
    ...prevUser,
    [field]: value,
  }));
};

// Updating state with arrays
const [items, setItems] = useState([]);

const addItem = (newItem) => {
  setItems((prevItems) => [...prevItems, newItem]);
};

const removeItem = (id) => {
  setItems((prevItems) => prevItems.filter((item) => item.id !== id));
};
```

### 2. Event Handlers

```javascript
const handleInputChange = (e) => {
  const { name, value } = e.target;
  setFormData((prev) => ({
    ...prev,
    [name]: value,
  }));
};

const handleSubmit = (e) => {
  e.preventDefault();
  // Process form data
};
```

### 3. Conditional Rendering

```javascript
const UserProfile = ({ user }) => {
  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      {user.email && <p>{user.email}</p>}
    </div>
  );
};
```

### 4. List Rendering

```javascript
const TodoList = ({ todos }) => {
  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
};
```

## Practice Exercises

### 1. Basic Functions

```javascript
// Write a function that takes two numbers and returns their sum
function add(a, b) {
  return a + b;
}

// Write a function that takes an array and returns the largest number
function findLargest(numbers) {
  return Math.max(...numbers);
}

// Write a function that takes a string and returns it reversed
function reverseString(str) {
  return str.split("").reverse().join("");
}
```

### 2. Array Manipulation

```javascript
// Write a function that filters even numbers from an array
function getEvenNumbers(numbers) {
  return numbers.filter((num) => num % 2 === 0);
}

// Write a function that doubles each number in an array
function doubleNumbers(numbers) {
  return numbers.map((num) => num * 2);
}

// Write a function that finds the sum of all numbers in an array
function sumNumbers(numbers) {
  return numbers.reduce((sum, num) => sum + num, 0);
}
```

### 3. Object Manipulation

```javascript
// Write a function that takes an object and returns an array of its values
function getObjectValues(obj) {
  return Object.values(obj);
}

// Write a function that merges two objects
function mergeObjects(obj1, obj2) {
  return { ...obj1, ...obj2 };
}

// Write a function that checks if an object has a specific property
function hasProperty(obj, prop) {
  return prop in obj;
}
```

### 4. Async Operations

```javascript
// Write a function that simulates fetching user data
async function fetchUser(id) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ id, name: `User ${id}`, email: `user${id}@example.com` });
    }, 1000);
  });
}

// Use the function
async function loadUser() {
  try {
    const user = await fetchUser(123);
    console.log("User loaded:", user);
  } catch (error) {
    console.error("Error loading user:", error);
  }
}
```

### 5. React-Style Patterns

```javascript
// Write a function that updates a user object
function updateUser(user, updates) {
  return { ...user, ...updates };
}

// Write a function that adds an item to a list
function addToList(list, item) {
  return [...list, item];
}

// Write a function that removes an item from a list
function removeFromList(list, id) {
  return list.filter((item) => item.id !== id);
}
```

Remember: The best way to learn JavaScript is by practicing. Try to solve these exercises and experiment with the code. Don't be afraid to make mistakes - that's how you learn!
