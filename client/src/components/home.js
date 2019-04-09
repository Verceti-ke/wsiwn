import React, { useState } from "react";

export default function() {
  const [count, setCount] = useState(0);

  return (
    <>
      <p>You clicked the button {count} times</p>
      <button onClick={() => setCount(count + 1)}>Click here</button>
    </>
  );
}
