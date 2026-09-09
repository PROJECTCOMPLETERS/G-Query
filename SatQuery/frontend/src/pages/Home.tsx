import { useEffect, useRef, useState } from "react";

import Navbar from "../components/layout/Navbar";
import QueryInput from "../components/query/QueryInput";
import QueryStatus from "../components/query/QueryStatus";
import SuggestedQueries from "../components/query/SuggestedQueries";

import ResultPanel, {
  type ChatMessage,
} from "../components/results/ResultPanel";

import {
  createDataset,
  getDataset,
  uploadDatasetFile,
} from "../api/datasetApi";

const Home = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [analyzing, setAnalyzing] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  const previewUrlsRef = useRef<string[]>([]);

  /*
   * Automatically scroll to the newest message.
   */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, analyzing]);

  /*
   * Clean up browser-generated preview URLs.
   */
  useEffect(() => {
    return () => {
      previewUrlsRef.current.forEach((url) => {
        URL.revokeObjectURL(url);
      });
    };
  }, []);

  const addMessage = (message: ChatMessage) => {
    setMessages((currentMessages) => [
      ...currentMessages,
      message,
    ]);
  };

  const handleAnalyze = async (
    userQuery: string,
    file: File | null
  ) => {
    if (analyzing) return;

    const cleanedQuery = userQuery.trim();

    const displayedQuery =
      cleanedQuery ||
      "Analyze this satellite image.";

    let imageUrl: string | undefined;

    /*
     * Create a browser preview only for formats
     * that the browser can display directly.
     *
     * GeoTIFF files are not displayed using
     * URL.createObjectURL() here.
     */
    if (
      file &&
      !/\.(tif|tiff)$/i.test(file.name)
    ) {
      imageUrl = URL.createObjectURL(file);

      previewUrlsRef.current.push(imageUrl);
    }

    const messageId = Date.now();

    /*
     * Add the user's message immediately.
     */
    const userMessage: ChatMessage = {
      id: messageId,
      role: "user",
      content: displayedQuery,
      fileName: file?.name,
      imageUrl,
    };

    addMessage(userMessage);

    setAnalyzing(true);

    try {
      /*
       * ==================================================
       * PHASE 1 BACKEND FLOW
       * ==================================================
       *
       * File
       *   ↓
       * Create Dataset
       *   ↓
       * Upload File
       *   ↓
       * Get Dataset
       *   ↓
       * Display Dataset
       */

      if (file) {
        /*
         * -----------------------------------------------
         * 1. Create Dataset
         * -----------------------------------------------
         *
         * POST /api/v1/datasets
         */
        const createdDataset = await createDataset(
          file.name,
          "single"
        );

        /*
         * -----------------------------------------------
         * 2. Upload File
         * -----------------------------------------------
         *
         * POST
         * /api/v1/datasets/{dataset_id}/files
         */
        await uploadDatasetFile(
          createdDataset.dataset_id,
          file
        );

        /*
         * -----------------------------------------------
         * 3. Retrieve Complete Dataset
         * -----------------------------------------------
         *
         * GET /api/v1/datasets/{dataset_id}
         *
         * This gives us the dataset including
         * the newly created observation.
         */
        const dataset = await getDataset(
          createdDataset.dataset_id
        );

        /*
         * -----------------------------------------------
         * 4. Display Backend Result
         * -----------------------------------------------
         */
        const assistantMessage: ChatMessage = {
          id: messageId + 1,
          role: "assistant",

          content: cleanedQuery
            ? "Your satellite dataset has been uploaded successfully. Query processing will be connected in Phase 2."
            : "Satellite image uploaded successfully. The dataset information is shown below.",

          dataset,

          /*
           * This is NOT a demo response.
           * The dataset came from the real backend.
           */
          demoMode: false,
        };

        addMessage(assistantMessage);

        return;
      }

      /*
       * ==================================================
       * QUERY-ONLY INPUT
       * ==================================================
       *
       * Phase 1 does not provide a query-processing
       * endpoint.
       *
       * Therefore we should NOT send a fake request
       * to the backend.
       *
       * For now we display an informational response.
       */

      const assistantMessage: ChatMessage = {
        id: messageId + 1,
        role: "assistant",

        content:
          "Query processing is not available yet. Phase 1 provides satellite dataset upload and management. Query understanding and analysis will be connected in Phase 2.",

        demoMode: false,
      };

      addMessage(assistantMessage);
    } catch (error) {
      /*
       * ==================================================
       * REAL BACKEND ERROR
       * ==================================================
       *
       * Do NOT fall back to mock analysis here.
       *
       * During integration we need to see real failures
       * such as:
       *
       * - Backend unavailable
       * - CORS problem
       * - Validation error
       * - Unsupported file
       * - Invalid dataset ID
       * - Storage failure
       */

      console.error(
        "SatQuery backend request failed:",
        error
      );

      const errorMessage: ChatMessage = {
        id: messageId + 1,
        role: "assistant",

        content:
          "I couldn't process your satellite dataset. Please check that the SatQuery backend is running and try again.",

        error: true,
        demoMode: false,
      };

      addMessage(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="app">
      <Navbar />

      <main className="chat-page">
        <div className="chat-scroll">
          {messages.length === 0 ? (
            <section className="welcome-section">
              <h1>How can SatQuery help?</h1>

              <p>
                Upload satellite imagery or ask a
                question to explore Earth observation
                data.
              </p>

              <SuggestedQueries
                onSelect={(selectedQuery) =>
                  handleAnalyze(
                    selectedQuery,
                    null
                  )
                }
              />
            </section>
          ) : (
            <ResultPanel messages={messages} />
          )}

          <QueryStatus
            analyzing={analyzing}
          />

          <div ref={chatEndRef} />
        </div>

        <QueryInput
          onAnalyze={handleAnalyze}
          analyzing={analyzing}
        />
      </main>
    </div>
  );
};

export default Home;