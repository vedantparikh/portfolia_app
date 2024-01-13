import React, { useEffect, useState } from "react";
console.log("Something went wrong")

const App = () => {
  console.log("Something went wrong");
  const [message, setMessage] = useState("");

  const getRootMessage = async () => {
    const requestOptions = {
      method: "GET",
      headers: {
        "accept": "application/json"
      }
    };
    const response = await fetch("http://localhost:8000/api", requestOptions);
    const data = await response.json();

    if (!response.ok) {
      console.log("something messed up");
    } else {
      setMessage(data.message);
    }

    console.log(data);
  };

  useEffect(() => {
    getRootMessage();
  }, []);

  return (
    <div>
      <h1>Hello Universe</h1>
    </div>
  );
};

export default App;
