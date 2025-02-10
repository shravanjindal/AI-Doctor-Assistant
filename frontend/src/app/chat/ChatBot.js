import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Save } from "lucide-react";
import ReactMarkdown from "react-markdown";
export default function ChatBot({ selectedChat, chats, setChats }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chatId, setChatId] = useState(null);

  useEffect(() => {
    if (selectedChat) {
      setChatId(selectedChat.id);
      setMessages(selectedChat.messages || []);
    } else {
      startNewChat();
    }
  }, [selectedChat]);

  const startNewChat = async () => {
    try {
      const response = await fetch("http://localhost:8000/start_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ title: "New Chat" }),
      });

      const data = await response.json();
      setChatId(data.chat_id);
      setChats([...chats, { id: data.chat_id, title: "New Chat", messages: [] }]);
    } catch (error) {
      console.error("Error starting chat:", error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
  
    const timestamp = new Date().toISOString();
    const userMessage = { sender: "user", text: input, timestamp };
  
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
  
    try {
      const response = await fetch("http://localhost:8000/save_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ chat_id: chatId, message: userMessage }),
      });
  
      const data = await response.json();
      if (data.llm_response) {
        setMessages((prev) => [...prev, data.llm_response]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };
  

  const saveChat = async () => {
    try {
      const response = await fetch("http://localhost:8000/end_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ chat_id: chatId }),
      });
  
      if (response.ok) {
        console.log("Chat saved successfully!");
        alert("Chat saved successfully!");
        startNewChat();  // Start a new chat after saving
        setMessages([]);
      } else {
        console.error("Error saving chat:", await response.text());
      }
    } catch (error) {
      console.error("Error saving chat:", error);
    }
  };
  

  return (
    <div className="flex flex-col h-screen mx-auto p-4 bg-gray-900 text-white rounded-lg shadow-lg border border-gray-700 custom-scrollbar">
      <h1 className="text-2xl font-semibold text-center mb-4 text-gray-200">
        AI-Powered Assistant
      </h1>
      <div className="flex-1 overflow-y-auto space-y-3 p-2 bg-gray-800 rounded-lg shadow-inner custom-scrollbar">
        {messages.map((msg, idx) => (
          <Card
            key={idx}
            className={`rounded-2xl p-3 shadow-md text-sm ${msg.sender === "user" ? "bg-gray-700 text-white ml-auto" : "bg-gray-200 "}`}
          >
            <CardContent>
              <p className="text-xs text-gray-400">{new Date(msg.timestamp).toLocaleTimeString()}</p>
              <ReactMarkdown className="mt-1">{msg.text}</ReactMarkdown>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex gap-3 mt-4 bg-gray-800 p-3 rounded-lg shadow-md">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 bg-gray-700 text-white border-none focus:ring-2 focus:ring-blue-400 rounded-lg p-2"
        />
        <Button onClick={() => { sendMessage(input); setInput(""); }} className="p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg shadow-md">
          <Send size={20} />
        </Button>
        <Button onClick={saveChat} className="bg-green-500 hover:bg-green-600 text-white rounded-lg shadow-md p-3 flex items-center justify-center">
          <Save size={20} className="mr-2" />
          Save Chat
        </Button>
      </div>
    </div>
  );
}
