import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { ReactNode } from 'react';

import {
  useChats,
  storageUnavailable,
} from '../../store/chatStore';

import logo from '../../assets/satquery-logo.jpeg';
import './ChatSidebar.css';

export type SidebarPanel =
  | 'history'
  | 'search'
  | 'files'
  | 'settings'
  | null;

interface Props {
  panel?: SidebarPanel;
  onPanelChange?: (panel: SidebarPanel) => void;

  // Supports the earlier Home.tsx props too.
  open?: boolean;
  onClose?: () => void;

  onNew?: () => void;
  onSelect?: (id: string) => void;
  onDelete?: (id: string) => void;
}

const icons: Record<string, ReactNode> = {
  new: (
    <>
      <path d="M12 5H6a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-6" />
      <path d="m16 3 5 5M10 14l-1 4 4-1L22 8a2.1 2.1 0 0 0-5-3Z" />
    </>
  ),

  files: (
    <>
      <rect x="3" y="7" width="14" height="14" rx="3" />
      <path d="M8 7V5a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2M3 17l4-4 4 4 3-3 3 3" />
      <circle cx="12" cy="11" r="1" />
    </>
  ),

  search: (
    <>
      <circle cx="10.5" cy="10.5" r="7.5" />
      <path d="m16 16 5 5" />
    </>
  ),

  history: (
    <path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5 9 9 0 0 1-4-.9L3 21l1.9-5.5a9 9 0 0 1-.9-4A8.5 8.5 0 0 1 12.5 3 8.5 8.5 0 0 1 21 11.5Z" />
  ),

  close: <path d="m6 6 12 12M6 18 18 6" />,

  more: (
    <>
      <circle cx="5" cy="12" r="1" />
      <circle cx="12" cy="12" r="1" />
      <circle cx="19" cy="12" r="1" />
    </>
  ),

  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5" />
    </>
  ),

  moon: (
    <path d="M20.8 13.5A9 9 0 0 1 10.5 3.2a9 9 0 1 0 10.3 10.3Z" />
  ),
};

function Icon({ name }: { name: string }) {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {icons[name]}
    </svg>
  );
}

const titles = {
  history: 'Your chats',
  search: 'Search chats',
  files: 'Uploaded files',
  settings: 'Preferences',
};

export default function ChatSidebar({
  panel: externalPanel,
  onPanelChange,
  open,
  onClose,
  onNew,
  onSelect,
  onDelete,
}: Props) {
  const store = useChats();

  const [localPanel, setLocalPanel] =
    useState<SidebarPanel>(null);

  const [search, setSearch] = useState('');
  const [menu, setMenu] = useState<string | null>(null);

  const rail = useRef<HTMLElement>(null);
  const searchInput = useRef<HTMLInputElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);

  const controlled =
    externalPanel !== undefined &&
    typeof onPanelChange === 'function';

  const panel: SidebarPanel = controlled
    ? externalPanel ?? null
    : localPanel;

  const changePanel = useCallback(
    (next: SidebarPanel) => {
      setLocalPanel(next);

      if (typeof onPanelChange === 'function') {
        onPanelChange(next);
      }

      if (next === null) {
        onClose?.();
      }
    },
    [onPanelChange, onClose]
  );

  // Compatibility with the previous open/onClose interface.
  useEffect(() => {
    if (controlled || typeof open !== 'boolean') return;

    setLocalPanel(open ? 'history' : null);
  }, [controlled, open]);

  // Focus only when the displayed panel changes.
  useEffect(() => {
    if (!panel) return;

    const frame = requestAnimationFrame(() => {
      if (panel === 'search') {
        searchInput.current?.focus();
      } else {
        closeButton.current?.focus();
      }
    });

    return () => cancelAnimationFrame(frame);
  }, [panel]);

  useEffect(() => {
    if (!panel) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;

      event.preventDefault();
      changePanel(null);

      rail.current
        ?.querySelector<HTMLButtonElement>(
          `[data-panel="${panel}"]`
        )
        ?.focus();
    };

    window.addEventListener('keydown', handleEscape);

    return () => {
      window.removeEventListener('keydown', handleEscape);
    };
  }, [panel, changePanel]);

  const query = search.trim().toLowerCase();

  // A conversation appears after its first message is sent.
  const chats = store.chats
    .filter(chat => chat.messages.length > 0)
    .sort(
      (a, b) =>
        Number(b.pinned) - Number(a.pinned) ||
        b.updated - a.updated
    );

  const matches =
    panel === 'search'
      ? chats.filter(chat =>
          [
            chat.title,
            ...chat.messages.map(message => message.content),
          ].some(text => text.toLowerCase().includes(query))
        )
      : chats;

  const files = chats.flatMap(chat =>
    chat.messages.flatMap(message =>
      message.fileName
        ? [
            {
              id: message.id,
              chatId: chat.id,
              title: chat.title,
              name: message.fileName,
            },
          ]
        : []
    )
  );

  function toggle(next: Exclude<SidebarPanel, null>) {
    setMenu(null);
    setSearch('');
    changePanel(panel === next ? null : next);
  }

  function closePanel() {
    changePanel(null);

    rail.current
      ?.querySelector<HTMLButtonElement>(
        `[data-panel="${panel}"]`
      )
      ?.focus();
  }

  function startNewChat() {
    setMenu(null);
    setSearch('');

    if (onNew) {
      onNew();
    } else {
      store.newChat();
    }

    changePanel(null);
  }

  function selectChat(id: string) {
    setMenu(null);
    setSearch('');

    if (onSelect) {
      onSelect(id);
    } else {
      store.select(id);
    }

    changePanel(null);
  }

  function renameChat(id: string, title: string) {
    const name = window.prompt('Conversation name', title);

    if (name?.trim()) {
      store.update(id, {
        title: name.trim().slice(0, 100),
      });
    }

    setMenu(null);
  }

  function deleteChat(id: string) {
    const confirmed = window.confirm(
      'Delete this conversation from this browser?'
    );

    if (!confirmed) return;

    if (onDelete) {
      onDelete(id);
    } else {
      store.remove(id);
    }

    setMenu(null);
  }

  return (
    <>
      <nav
        className="gq-rail"
        aria-label="Chat navigation"
        ref={rail}
      >
        <button
          type="button"
          className="gq-rail-button gq-brand"
          onClick={startNewChat}
          aria-label="G-Query — new chat"
          title="G-Query — new chat"
        >
          <img src={logo} alt="" />
          <span className="gq-tooltip">New chat</span>
        </button>

        <div className="gq-rail-actions">
          <button
            type="button"
            className="gq-rail-button"
            onClick={startNewChat}
            aria-label="New chat"
            title="New chat"
          >
            <Icon name="new" />
            <span className="gq-tooltip">New chat</span>
          </button>

          {(['files', 'search', 'history'] as const).map(item => (
            <button
              type="button"
              key={item}
              className={`gq-rail-button ${
                panel === item ? 'is-active' : ''
              }`}
              data-panel={item}
              onClick={() => toggle(item)}
              aria-label={titles[item]}
              title={titles[item]}
              aria-expanded={panel === item}
              aria-controls={
                panel === item ? 'gq-sidebar-panel' : undefined
              }
            >
              <Icon name={item} />

              <span className="gq-tooltip">
                {titles[item]}
              </span>
            </button>
          ))}
        </div>

        <button
          type="button"
          className={`gq-rail-button gq-profile ${
            panel === 'settings' ? 'is-active' : ''
          }`}
          data-panel="settings"
          onClick={() => toggle('settings')}
          aria-label="Preferences"
          title="Preferences"
          aria-expanded={panel === 'settings'}
          aria-controls={
            panel === 'settings'
              ? 'gq-sidebar-panel'
              : undefined
          }
        >
          <span className="gq-avatar" aria-hidden="true">
            GQ
          </span>

          <span className="gq-tooltip">Preferences</span>
        </button>
      </nav>

      {panel && (
        <>
          <button
            type="button"
            className="gq-drawer-backdrop"
            onClick={closePanel}
            aria-label="Close sidebar"
            tabIndex={-1}
          />

          <aside
            className="gq-drawer"
            id="gq-sidebar-panel"
            aria-label={titles[panel]}
          >
            <div className="gq-drawer-heading">
              <h2>{titles[panel]}</h2>

              <button
                type="button"
                ref={closeButton}
                className="gq-icon-button"
                onClick={closePanel}
                aria-label="Close panel"
              >
                <Icon name="close" />
              </button>
            </div>

            {panel === 'search' && (
              <div className="gq-search-field">
                <Icon name="search" />

                <input
                  ref={searchInput}
                  value={search}
                  onChange={event =>
                    setSearch(event.target.value)
                  }
                  placeholder="Search your chats…"
                  aria-label="Search chat titles and messages"
                />
              </div>
            )}

            {(panel === 'history' || panel === 'search') && (
              <>
                <button
                  type="button"
                  className="gq-new-chat"
                  onClick={startNewChat}
                >
                  <Icon name="new" />
                  New chat
                </button>

                <div className="gq-panel-scroll">
                  {matches.map(chat => (
                    <div
                      key={chat.id}
                      className={`gq-chat-row ${
                        store.activeId === chat.id
                          ? 'is-current'
                          : ''
                      }`}
                    >
                      <div className="gq-chat-line">
                        <button
                          type="button"
                          className="gq-chat-link"
                          onClick={() => selectChat(chat.id)}
                          title={chat.title}
                          aria-current={
                            store.activeId === chat.id
                              ? 'page'
                              : undefined
                          }
                        >
                          <span>
                            {chat.pinned && (
                              <span aria-label="Pinned">
                                ★{' '}
                              </span>
                            )}

                            {chat.title || 'Untitled chat'}
                          </span>

                          {panel === 'search' && (
                            <small>
                              {chat.messages
                                .find(message =>
                                  message.content
                                    .toLowerCase()
                                    .includes(query)
                                )
                                ?.content.slice(0, 90)}
                            </small>
                          )}
                        </button>

                        <button
                          type="button"
                          className="gq-icon-button gq-more"
                          aria-label={`Options for ${chat.title}`}
                          aria-expanded={menu === chat.id}
                          onClick={() =>
                            setMenu(
                              menu === chat.id ? null : chat.id
                            )
                          }
                        >
                          <Icon name="more" />
                        </button>
                      </div>

                      {menu === chat.id && (
                        <div className="gq-chat-actions">
                          <button
                            type="button"
                            onClick={() => {
                              store.update(chat.id, {
                                pinned: !chat.pinned,
                              });
                              setMenu(null);
                            }}
                          >
                            {chat.pinned ? 'Unpin' : 'Pin'}
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              renameChat(chat.id, chat.title)
                            }
                          >
                            Rename
                          </button>

                          <button
                            type="button"
                            className="gq-delete"
                            onClick={() => deleteChat(chat.id)}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  ))}

                  {!matches.length && (
                    <p className="gq-empty" role="status">
                      {panel === 'search' && query
                        ? 'No matching chats.'
                        : 'Send your first message. Your conversation will appear here automatically.'}
                    </p>
                  )}
                </div>

                <p
                  className="gq-panel-note"
                  role={
                    storageUnavailable() ? 'alert' : undefined
                  }
                >
                  {storageUnavailable()
                    ? 'Chat history could not be saved. Browser storage is unavailable or full.'
                    : 'Chats are saved automatically in this browser.'}
                </p>
              </>
            )}

            {panel === 'files' && (
              <div className="gq-panel-scroll">
                <p className="gq-panel-note">
                  Select a filename to open its conversation.
                </p>

                {files.map(file => (
                  <button
                    type="button"
                    className="gq-file-link"
                    key={`${file.chatId}-${file.id}`}
                    onClick={() => selectChat(file.chatId)}
                  >
                    <Icon name="files" />

                    <span>
                      <strong>{file.name}</strong>
                      <small>{file.title}</small>
                    </span>
                  </button>
                ))}

                {!files.length && (
                  <p className="gq-empty">
                    Attach a file using the + button in the
                    message box, then send your message.
                    Its filename will appear here.
                  </p>
                )}
              </div>
            )}

            {panel === 'settings' && (
              <div className="gq-panel-scroll">
                <p className="gq-setting-label">
                  Appearance
                </p>

                <button
                  type="button"
                  className="gq-theme-button"
                  onClick={() =>
                    store.setTheme(
                      store.theme === 'dark' ? 'light' : 'dark'
                    )
                  }
                >
                  <Icon
                    name={
                      store.theme === 'dark' ? 'sun' : 'moon'
                    }
                  />

                  Switch to{' '}
                  {store.theme === 'dark' ? 'light' : 'dark'} mode
                </button>

                <p className="gq-panel-note">
                  Your appearance preference and chat history
                  are saved in this browser.
                </p>
              </div>
            )}
          </aside>
        </>
      )}
    </>
  );
}