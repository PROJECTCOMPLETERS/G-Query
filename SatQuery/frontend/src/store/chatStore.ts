import { create } from "zustand";
import {
  persist,
  createJSONStorage,
} from "zustand/middleware";

import type {
  Chat,
  ChatMessage,
} from "../types/query";

let storageFailed = false;

const storage = {
  getItem: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch {
      storageFailed = true;
      return null;
    }
  },

  setItem: (key: string, value: string): void => {
    try {
      localStorage.setItem(key, value);
    } catch {
      storageFailed = true;
    }
  },

  removeItem: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch {
      storageFailed = true;
    }
  },
};

export const storageUnavailable = (): boolean => {
  return storageFailed;
};

interface ChatState {
  chats: Chat[];
  activeId: string | null;
  theme: "dark" | "light";

  newChat: () => string;

  select: (id: string) => void;

  update: (
    id: string,
    patch: Partial<Chat>
  ) => void;

  add: (
    id: string,
    message: ChatMessage
  ) => void;

  patch: (
    id: string,
    messageId: string,
    patch: Partial<ChatMessage>
  ) => void;

  remove: (id: string) => void;

  setTheme: (
    theme: "dark" | "light"
  ) => void;
}

export const useChats = create<ChatState>()(
  persist(
    (set, get) => ({
      chats: [],
      activeId: null,
      theme: "dark",

      newChat: () => {
        const id = crypto.randomUUID();

        const newConversation: Chat = {
          id,
          title: "New chat",
          updated: Date.now(),
          pinned: false,
          messages: [],
          observationIds: [],
        };

        set((state) => ({
          activeId: id,
          chats: [
            newConversation,
            ...state.chats,
          ],
        }));

        return id;
      },

      select: (id) => {
        set({
          activeId: id,
        });
      },

      update: (id, patch) => {
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.id === id
              ? {
                  ...chat,
                  ...patch,
                  updated: Date.now(),
                }
              : chat
          ),
        }));
      },

      add: (id, message) => {
        const chat = get().chats.find(
          (item) => item.id === id
        );

        if (!chat) return;

        get().update(id, {
          messages: [
            ...chat.messages,
            message,
          ],

          title:
            chat.messages.length > 0
              ? chat.title
              : message.content.slice(0, 45),
        });
      },

      patch: (id, messageId, patch) => {
        const chat = get().chats.find(
          (item) => item.id === id
        );

        if (!chat) return;

        get().update(id, {
          messages: chat.messages.map(
            (message) =>
              message.id === messageId
                ? {
                    ...message,
                    ...patch,
                  }
                : message
          ),
        });
      },

      remove: (id) => {
        set((state) => ({
          chats: state.chats.filter(
            (chat) => chat.id !== id
          ),

          activeId:
            state.activeId === id
              ? null
              : state.activeId,
        }));
      },

      setTheme: (theme) => {
        set({ theme });
      },
    }),
    {
      name: "g-query-conversations-v2",
      version: 1,

      storage: createJSONStorage(
        () => storage
      ),

      partialize: (state) => ({
        chats: state.chats,
        activeId: state.activeId,
        theme: state.theme,
      }),

      onRehydrateStorage: () => {
        return (_state, error) => {
          if (error) {
            storageFailed = true;
          }
        };
      },
    }
  )
);