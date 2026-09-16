import { useState } from "react";
import { useChats } from "../../store/chatStore";

interface Props {
  open: boolean;
  onClose: () => void;
  onNew: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function ChatSidebar({
  open,
  onClose,
  onNew,
  onSelect,
  onDelete,
}: Props) {
  const store = useChats();
  const [search, setSearch] = useState("");

  const chats = store.chats
    .filter((chat) => {
      const searchable = [
        chat.title,
        ...chat.messages.map((message) => message.content),
      ].join(" ");

      return (
        chat.messages.length > 0 &&
        searchable.toLowerCase().includes(search.toLowerCase())
      );
    })
    .sort(
      (a, b) =>
        Number(b.pinned) - Number(a.pinned) ||
        b.updated - a.updated
    );

  return (
    <>
      {open && (
        <button
          className="sidebar-backdrop"
          aria-label="Close history"
          onClick={onClose}
        />
      )}

      <aside
        className={`chat-sidebar ${open ? "open" : ""}`}
        aria-label="Conversation history"
      >
        <div className="sidebar-heading">
          <strong>Your conversations</strong>

          <button
            onClick={onClose}
            aria-label="Close sidebar"
          >
            ×
          </button>
        </div>

        <button className="sidebar-new" onClick={onNew}>
          ＋ New chat
        </button>

        <input
          aria-label="Search chats"
          placeholder="Search chats…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <div className="chat-list">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${
                store.activeId === chat.id ? "active" : ""
              }`}
            >
              <button
                className="chat-title"
                onClick={() => onSelect(chat.id)}
              >
                {chat.pinned ? "★ " : ""}
                {chat.title}
              </button>

              <div className="chat-item-actions">
                <button
                  onClick={() =>
                    store.update(chat.id, {
                      pinned: !chat.pinned,
                    })
                  }
                >
                  {chat.pinned ? "Unpin" : "Pin"}
                </button>

                <button
                  onClick={() => {
                    const name = window.prompt(
                      "Conversation name",
                      chat.title
                    );

                    if (name?.trim()) {
                      store.update(chat.id, {
                        title: name.trim().slice(0, 100),
                      });
                    }
                  }}
                >
                  Rename
                </button>

                <button
                  onClick={() => {
                    if (
                      window.confirm(
                        "Delete this conversation from this browser?"
                      )
                    ) {
                      onDelete(chat.id);
                    }
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}

          {!chats.length && (
            <p className="sidebar-empty">
              {search
                ? "No matching conversations."
                : "Your chats will appear here."}
            </p>
          )}
        </div>

        <button
          className="theme-button"
          onClick={() =>
            store.setTheme(
              store.theme === "dark" ? "light" : "dark"
            )
          }
        >
          {store.theme === "dark" ? "Light" : "Dark"} appearance
        </button>

        <small>History is saved in this browser.</small>
      </aside>
    </>
  );
}