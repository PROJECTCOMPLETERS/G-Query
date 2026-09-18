import { useEffect, useRef, useState } from "react";

import Navbar from "../components/layout/Navbar";
import QueryInput from "../components/query/QueryInput";
import SuggestedQueries from "../components/query/SuggestedQueries";
import ResultPanel from "../components/results/ResultPanel";
import ChatSidebar from "../components/chat/ChatSidebar";
import DatasetSelector from "../components/chat/DatasetSelector";

import {
  createDataset,
  getDataset,
  uploadDatasetFile,
} from "../api/datasetApi";

import {
  submitQuery,
  clarifyQuery,
  retryQuery,
  followQuery,
  queryCapabilities,
  queryFailure,
} from "../api/queryApi";

import {
  useChats,
  storageUnavailable,
} from "../store/chatStore";

import type {
  ChatMessage,
  QueryInput as Input,
  QueryResponse,
} from "../types/query";

import type { DatasetType } from "../types/dataset";

import "../chat.css";

export default function Home() {
  const store = useChats();

  const chat = store.chats.find(
    (item) => item.id === store.activeId
  );

  const [busy, setBusy] = useState(false);
  const [sidebar, setSidebar] = useState(
    () => window.innerWidth > 850
  );
  const [showData, setShowData] = useState(false);
  const [draft, setDraft] = useState("");
  const [edit, setEdit] = useState<ChatMessage | null>(null);
  const [uploadType, setUploadType] =
    useState<DatasetType>("single");

  const scrollRef = useRef<HTMLDivElement>(null);
  const stickToBottom = useRef(true);

  const job = useRef<{
    controller: AbortController;
    cid: string;
    mid: string;
  } | null>(null);

  const latest = [...(chat?.messages || [])]
    .reverse()
    .find((message) => message.role === "assistant");

  const needsAnswer =
    latest?.response?.status === "NEEDS_CLARIFICATION" &&
    !latest.stopped &&
    !edit;

  const blocked =
    !!needsAnswer &&
    (!queryCapabilities.clarify || !latest?.response?.question);

  useEffect(() => {
    document.documentElement.dataset.theme = store.theme;
  }, [store.theme]);

  useEffect(() => {
    if (stickToBottom.current) {
      scrollRef.current?.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [chat?.messages]);

  useEffect(() => {
    return () => {
      const active = job.current;

      if (active) {
        active.controller.abort();

        useChats.getState().patch(
          active.cid,
          active.mid,
          { stopped: true }
        );
      }
    };
  }, []);

  function stop() {
    const active = job.current;

    if (active) {
      active.controller.abort();

      store.patch(active.cid, active.mid, {
        stopped: true,
      });
    }

    job.current = null;
    setBusy(false);
  }

  function changeChat(id?: string) {
    stop();

    setDraft("");
    setEdit(null);
    setShowData(false);
    stickToBottom.current = true;

    if (id) {
      store.select(id);
    } else {
      store.newChat();
    }

    if (window.innerWidth <= 850) {
      setSidebar(false);
    }
  }

  useEffect(() => {
    const shortcut = (event: KeyboardEvent) => {
      if (
        (event.ctrlKey || event.metaKey) &&
        event.key.toLowerCase() === "k"
      ) {
        event.preventDefault();
        changeChat();
      }
    };

    window.addEventListener("keydown", shortcut);

    return () =>
      window.removeEventListener("keydown", shortcut);
  });

  async function execute(
    cid: string,
    mid: string,
    input: Input,
    start: (signal: AbortSignal) => Promise<QueryResponse>
  ) {
    const controller = new AbortController();

    job.current = { controller, cid, mid };
    setBusy(true);

    let requestId = input.request_id;

    try {
      const first = await start(controller.signal);
      requestId = first.request_id;

      const notice = await followQuery(
        first,
        (response) => {
          if (controller.signal.aborted) return;

          store.patch(cid, mid, {
            response,

            input: {
              ...input,
              request_id: response.request_id,
            },

            content:
              response.status === "COMPLETED"
                ? String(
                    response.result?.text ||
                      response.result?.answer ||
                      ""
                  )
                : "",

            stopped: false,
            notice: undefined,
          });
        },
        controller.signal
      );

      if (!controller.signal.aborted && notice) {
        store.patch(cid, mid, { notice });
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        store.patch(cid, mid, {
          response: queryFailure(error, requestId),
        });
      }
    } finally {
      if (job.current?.controller === controller) {
        job.current = null;
        setBusy(false);
      }
    }
  }

  async function send(text: string, file: File | null) {
    if (
      job.current ||
      blocked ||
      (!text.trim() && !file)
    ) {
      return;
    }

    let cid = store.activeId || store.newChat();

    // Preserve the original conversation when editing.
    if (edit && chat) {
      cid = store.newChat();

      store.update(cid, {
        dataset: chat.dataset,
        observationIds: chat.observationIds,
        title: `${chat.title} (edited)`,

        messages: chat.messages.slice(
          0,
          chat.messages.findIndex(
            (message) => message.id === edit.id
          )
        ),
      });

      setEdit(null);
    }

    const current = useChats
      .getState()
      .chats.find((item) => item.id === cid)!;

    const last = [...current.messages]
      .reverse()
      .find((message) => message.role === "assistant");

    const clarification =
      last?.response?.status === "NEEDS_CLARIFICATION" &&
      !last.stopped
        ? last.response.request_id
        : undefined;

    const input: Input = {
      request_id: clarification || crypto.randomUUID(),

      question:
        text.trim() || "Analyze this satellite image.",

      inputs: current.observationIds.map((input_id) => ({
        input_id,
        type: "image",
      })),
    };

    store.add(cid, {
      id: crypto.randomUUID(),
      role: "user",
      content: input.question,
      fileName: file?.name,
    });

    const mid = crypto.randomUUID();

    store.add(cid, {
      id: mid,
      role: "assistant",
      content: "",
      input,
    });

    stickToBottom.current = true;

    await execute(cid, mid, input, async (signal) => {
      let dataset = current.dataset;

      if (file) {
        if (!dataset) {
          dataset = await createDataset(
            file.name,
            uploadType,
            signal
          );
        }

        // Keep the dataset ID even if the upload fails.
        if (!signal.aborted) {
          store.update(cid, { dataset });
        }

        await uploadDatasetFile(
          dataset.dataset_id,
          file,
          signal
        );

        dataset = await getDataset(
          dataset.dataset_id,
          signal
        );

        if (signal.aborted) {
          throw new DOMException("Aborted", "AbortError");
        }

        input.inputs = dataset.observations.map(
          (observation) => ({
            input_id: observation.observation_id,
            type: "image",
          })
        );

        store.update(cid, {
          dataset,
          observationIds: input.inputs.map(
            (observation) => observation.input_id
          ),
        });

        store.patch(cid, mid, {
          dataset,
          input,
        });
      }

      if (clarification) {
        input.question =
          `${last?.input?.question || ""}\nClarification: ${text}`;

        return clarifyQuery(
          clarification,
          text,
          input.inputs,
          signal
        );
      }

      return submitQuery(input, signal);
    });
  }

  async function retry(message: ChatMessage) {
    if (
      job.current ||
      !chat ||
      !message.response?.error?.recoverable ||
      !queryCapabilities.retry ||
      !message.input
    ) {
      return;
    }

    await execute(
      chat.id,
      message.id,
      message.input,
      (signal) =>
        retryQuery(message.response!.request_id, signal)
    );
  }

  async function regenerate(message: ChatMessage) {
    if (job.current || !chat || !message.input) return;

    const input: Input = {
      ...message.input,
      request_id: crypto.randomUUID(),
    };

    const mid = crypto.randomUUID();

    store.add(chat.id, {
      id: mid,
      role: "assistant",
      content: "",
      input,
    });

    await execute(chat.id, mid, input, (signal) =>
      submitQuery(input, signal)
    );
  }

  function exportChat() {
    if (!chat) return;

    const content = chat.messages
      .map(
        (message) =>
          `## ${message.role}\n\n${
            message.content ||
            message.response?.question ||
            message.response?.reason ||
            message.response?.status ||
            ""
          }`
      )
      .join("\n\n");

    const url = URL.createObjectURL(
      new Blob([content], {
        type: "text/markdown",
      })
    );

    const link = document.createElement("a");
    link.href = url;
    link.download = `satquery-${chat.id}.md`;
    link.click();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <div className="app">
      <Navbar
        onNew={() => changeChat()}
        onHistory={() => setSidebar((value) => !value)}
        onAbout={() =>
          window.alert(
            "G-Query AI — satellite queries, datasets and observations. Real analysis depends on the connected backend."
          )
        }
      />

      <div
        className={`chat-layout ${
          sidebar ? "with-sidebar" : ""
        }`}
      >
        <ChatSidebar
          open={sidebar}
          onClose={() => setSidebar(false)}
          onNew={() => changeChat()}
          onSelect={changeChat}
          onDelete={(id) => {
            if (store.activeId === id) stop();
            store.remove(id);
          }}
        />

        <main className="chat-page">
          <div className="chat-toolbar">
            <button
              onClick={() => setShowData((value) => !value)}
            >
              {chat?.dataset?.name || "Select dataset"}
            </button>

            <span>
              {chat?.observationIds.length || 0} observations
            </span>

            <button
              disabled={!chat?.messages.length}
              onClick={exportChat}
            >
              Export chat
            </button>
          </div>

          {storageUnavailable() && (
            <p role="alert">
              Browser history could not be saved.
              Storage is unavailable or full.
            </p>
          )}

          {showData && (
            <DatasetSelector
              dataset={chat?.dataset}
              ids={chat?.observationIds || []}
              busy={busy}
              uploadType={uploadType}
              onUploadType={setUploadType}
              onChange={(dataset, observationIds) => {
                const id =
                  store.activeId || store.newChat();

                store.update(id, {
                  dataset,
                  observationIds,
                });
              }}
            />
          )}

          <div
            className="chat-scroll"
            ref={scrollRef}
            onScroll={(event) => {
              const element = event.currentTarget;

              stickToBottom.current =
                element.scrollHeight -
                  element.scrollTop -
                  element.clientHeight <
                100;
            }}
          >
            {!chat?.messages.length ? (
              <section className="welcome-section">
                <h1>How can SatQuery help?</h1>

                <p>
                  Upload satellite imagery or ask a question
                  about your observations.
                </p>

                <SuggestedQueries onSelect={setDraft} />
              </section>
            ) : (
              <ResultPanel
                messages={chat.messages}
                busy={busy}
                onRetry={retry}
                onRegenerate={regenerate}
                onData={() => setShowData(true)}
                onAnswer={(answer) => {
                  void send(answer, null);
                }}
                onEdit={(message) => {
                  setEdit(message);
                  setDraft(message.content);
                }}
                onFeedback={(id, feedback) =>
                  store.patch(chat.id, id, { feedback })
                }
              />
            )}
          </div>

          {edit && (
            <p className="edit-notice">
              Editing creates a separate chat.
              Reattach the image if needed.{" "}

              <button
                onClick={() => {
                  setEdit(null);
                  setDraft("");
                }}
              >
                Cancel edit
              </button>
            </p>
          )}

          <QueryInput
            key={store.activeId || "new"}
            query={draft}
            onQuery={setDraft}
            onAnalyze={send}
            analyzing={busy}
            onStop={stop}
            clarification={!!needsAnswer}
            blocked={blocked}
          />
        </main>
      </div>
    </div>
  );
}