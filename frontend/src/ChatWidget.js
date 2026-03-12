import React, { useState } from "react";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "bot", text: "請輸入想去的地方與天數，例如：東京三日遊、韓國六日親子行程、北海道溫泉行" },
  ]);
  const [input, setInput] = useState("");

  const toggleOpen = () => setOpen(!open);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { from: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");

    try {
      const res = await fetch("/chatbot/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();

      const newMsgs = [];

      // 先顯示 reply 文字回應
      if (data.reply) {
        newMsgs.push({ from: "bot", text: data.reply });
      }

      // 再顯示推薦行程卡片
      if (data.recommended_trips && data.recommended_trips.length > 0) {
        data.recommended_trips.forEach((trip) => {
          newMsgs.push({
            from: "bot",
            isCard: true,
            trip: trip,
          });
        });
      }

      if (newMsgs.length === 0) {
        newMsgs.push({ from: "bot", text: "抱歉，找不到符合的行程。" });
      }

      setMessages((msgs) => [...msgs, ...newMsgs]);
    } catch {
      setMessages((msgs) => [...msgs, { from: "bot", text: "伺服器錯誤，請稍後再試。" }]);
    }
  };

  const TripCard = ({ trip }) => (
    <div style={{
      backgroundColor: "#f0f7ff",
      border: "1px solid #b3d4ff",
      borderRadius: 10,
      padding: "10px 12px",
      maxWidth: "80%",
      textAlign: "left",
    }}>
      <div style={{ fontWeight: "bold", marginBottom: 4, color: "#1a1a1a" }}>
        {trip.name}
      </div>
      <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
        {trip.city}, {trip.country} · {trip.duration} 天
      </div>
      <a
        href={trip.link}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "inline-block",
          backgroundColor: "#0084ff",
          color: "white",
          padding: "4px 12px",
          borderRadius: 12,
          fontSize: 12,
          textDecoration: "none",
        }}
      >
        查看詳情 →
      </a>
    </div>
  );

  return (
    <>
      {open && (
        <div style={{
          position: "fixed",
          bottom: 80,
          right: 20,
          width: 320,
          height: 420,
          boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
          borderRadius: 12,
          backgroundColor: "white",
          fontFamily: "Arial, sans-serif",
          display: "flex",
          flexDirection: "column",
          zIndex: 9999,
          overflow: "hidden",
        }}>
          {/* 標題列 */}
          <div style={{
            backgroundColor: "#0084ff",
            color: "white",
            padding: "12px 16px",
            fontWeight: "bold",
            fontSize: 14,
          }}>
            旅遊小幫手
          </div>

          {/* 訊息區 */}
          <div style={{
            flex: 1,
            overflowY: "auto",
            padding: 12,
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                display: "flex",
                justifyContent: m.from === "user" ? "flex-end" : "flex-start",
              }}>
                {m.isCard ? (
                  <TripCard trip={m.trip} />
                ) : (
                  <span style={{
                    display: "inline-block",
                    padding: "8px 12px",
                    borderRadius: 16,
                    backgroundColor: m.from === "user" ? "#0084ff" : "#eee",
                    color: m.from === "user" ? "white" : "#1a1a1a",
                    maxWidth: "80%",
                    fontSize: 13,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}>
                    {m.text}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* 輸入區 */}
          <div style={{
            padding: "10px 12px",
            borderTop: "1px solid #eee",
            display: "flex",
            gap: 8,
          }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              style={{
                flex: 1,
                padding: "8px 10px",
                borderRadius: 20,
                border: "1px solid #ddd",
                fontSize: 13,
                outline: "none",
              }}
              placeholder="輸入訊息..."
            />
            <button
              onClick={sendMessage}
              style={{
                backgroundColor: "#0084ff",
                color: "white",
                border: "none",
                borderRadius: 20,
                padding: "8px 14px",
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              送出
            </button>
          </div>
        </div>
      )}

      <button
        onClick={toggleOpen}
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          width: 56,
          height: 56,
          borderRadius: "50%",
          backgroundColor: "#0084ff",
          border: "none",
          color: "white",
          fontSize: 26,
          cursor: "pointer",
          zIndex: 10000,
          boxShadow: "0 2px 10px rgba(0,132,255,0.4)",
        }}
        title="旅遊小幫手"
      >
        
      </button>
    </>
  );
}
