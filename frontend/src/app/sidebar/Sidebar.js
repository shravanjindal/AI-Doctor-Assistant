"use client";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

const Sidebar = ({ chats, setChats, onSelectChat }) => {
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await fetch("http://localhost:8000/chats", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        });
        const data = await response.json();
        setChats(data);
      } catch (error) {
        console.error("Error fetching chats:", error);
      }
    };

    fetchChats();
    const interval = setInterval(fetchChats, 5000);
    return () => clearInterval(interval);
  }, [setChats]);

  // Function to start a new chat
  const startNewChat = async () => {
    try {
      const response = await fetch("http://localhost:8000/start_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ title: "Chat" }),
      });

      const data = await response.json();
      onSelectChat({ id: data.chat_id, title: "Chat", messages: [] });
    } catch (error) {
      console.error("Error starting chat:", error);
    }
  };

  return (
    <div className="w-full h-screen bg-gray-900 text-white p-6 overflow-y-auto shadow-lg border-r border-gray-700 custom-scrollbar">
      <div className="flex items-center justify-between mb-6 p-4 bg-gray-800 rounded-lg shadow-md">
        <Button
          onClick={async () => {
            try {
              const response = await fetch("http://localhost:8000/logout", {
                method: "GET",
                credentials: "include",
              });

              if (response.ok) {
                window.location.reload();
              } else {
                console.error("Logout failed");
              }
            } catch (error) {
              console.error("Error logging out:", error);
            }
          }}
        >
          Logout
        </Button>

        <Button onClick={startNewChat} className="flex items-center gap-x-2">
          New Chat
          <i className="fa-solid fa-plus text-lg"></i>
        </Button>
      </div>

      <ul className="space-y-2" aria-label="Chat List">
        {chats.map((chat, index) => (
          <li
            key={chat.id || index}
            className="p-3 bg-gray-800 rounded-lg text-gray-200 hover:bg-gray-700 cursor-pointer transition duration-200"
            onClick={() => onSelectChat(chat)}
            title={`Chat ID: ${chat.id || "Unknown ID"}`}
          >
            <strong>{chat.title || "Chat"}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
