import { useEffect, useRef, useState } from "react";

import Navbar from "../components/layout/Navbar";
import QueryInput from "../components/query/QueryInput";
import QueryStatus from "../components/query/QueryStatus";
import SuggestedQueries from "../components/query/SuggestedQueries";

import ResultPanel, {
  type ChatMessage,
} from "../components/results/ResultPanel";

import {
  getDataset,
  submitQuery,
  uploadSatelliteFile,
} from "../api/datasetApi";

import { runMockAnalysis } from "../components/services/mockAnalysis";

const Home = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [analyzing, setAnalyzing] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const previewUrlsRef = useRef<string[]>([]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, analyzing]);

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

    if (file && !/\.(tif|tiff)$/i.test(file.name)) {
      imageUrl = URL.createObjectURL(file);
      previewUrlsRef.current.push(imageUrl);
    }

    const messageId = Date.now();

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
      let datasetId: string | undefined;
      let uploadedDataset = undefined;

      /*
       * REAL BACKEND FLOW
       */

      if (file) {
        const uploadResponse =
          await uploadSatelliteFile(file);

        if (!uploadResponse.success) {
          throw new Error(
            uploadResponse.message ||
              "Satellite image upload failed."
          );
        }

        datasetId = uploadResponse.dataset_id;
        uploadedDataset = uploadResponse.dataset;

        if (!uploadedDataset && datasetId) {
          uploadedDataset =
            await getDataset(datasetId);
        }
      }

      if (cleanedQuery) {
        const queryResponse = await submitQuery(
          cleanedQuery,
          datasetId
        );

        if (!queryResponse.success) {
          throw new Error(
            "SatQuery could not process this query."
          );
        }

        const assistantMessage: ChatMessage = {
          id: messageId + 1,
          role: "assistant",
          content: queryResponse.answer,
          dataset:
            queryResponse.dataset ||
            uploadedDataset,
          demoMode: false,
        };

        addMessage(assistantMessage);
      } else {
        const assistantMessage: ChatMessage = {
          id: messageId + 1,
          role: "assistant",
          content:
            "Satellite image uploaded successfully. The dataset information is shown below.",
          dataset: uploadedDataset,
          demoMode: false,
        };

        addMessage(assistantMessage);
      }
    } catch {
      /*
       * DEMO MODE FALLBACK
       *
       * Backend unavailable / request failed na
       * error kaattaama built-in demo response use pannum.
       */

      const demoResponse = await runMockAnalysis(
        displayedQuery,
        file
      );

      const demoMessage: ChatMessage = {
        id: messageId + 1,
        role: "assistant",
        content: demoResponse.answer,
        dataset: demoResponse.dataset,
        demoMode: true,
      };

      addMessage(demoMessage);
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
                Upload satellite imagery or ask a question
                to explore Earth observation data.
              </p>

              <SuggestedQueries
                onSelect={(selectedQuery) =>
                  handleAnalyze(selectedQuery, null)
                }
              />
            </section>
          ) : (
            <ResultPanel messages={messages} />
          )}

          <QueryStatus analyzing={analyzing} />

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