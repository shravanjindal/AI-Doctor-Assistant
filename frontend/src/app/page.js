"use client";
import { useState, useEffect } from "react";
import Sidebar from "./sidebar/Sidebar";
import ChatBot from "./chat/ChatBot";
import Login from "./auth/Login";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("http://localhost:8000/auth/check", { credentials: "include" });
        if (response.ok) {
          setIsLoggedIn(true);
        } else {
          setIsLoggedIn(false);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        setIsLoggedIn(false);
      }
    };

    checkAuth();
  }, []);

  return (
    <>
      {!isLoggedIn ? (
        <Login onLogin={() => setIsLoggedIn(true)} />
      ) : (
        <div className="grid grid-cols-[1fr_3fr] h-screen">
          <div className="bg-gray-900 text-white p-4">
            <Sidebar chats={chats} setChats={setChats} onSelectChat={setSelectedChat} />
          </div>
          <div className="bg-gray-900 p-4">
            <ChatBot selectedChat={selectedChat} chats={chats} setChats={setChats} />
          </div>
        </div>
      )}
    </>
  );
}
