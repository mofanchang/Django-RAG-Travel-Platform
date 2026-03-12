// frontend/src/App.js

import React from "react";
import ChatWidget from "./ChatWidget";
import './App.css';      // 套用 .App 的背景樣式等
import './Test.css';     // 套用 .test 用來測試 CSS 是否會出現在 build

export default function App() {
  return (
    <div className="App">
      <h1 className="test">旅遊小幫手</h1> {/* 加上 .test class 測試 CSS */}
      <ChatWidget />
    </div>
  );
}
