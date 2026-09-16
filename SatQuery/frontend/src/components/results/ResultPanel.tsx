import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import DatasetInfo from './DatasetInfo';
import MapView from '../map/MapView';
import QueryStatus from '../query/QueryStatus';

import type { ChatMessage } from '../../types/query';

export type { ChatMessage } from '../../types/query';

interface Props {
  messages: ChatMessage[];
  busy: boolean;
  onRetry: (message: ChatMessage) => void;
  onRegenerate: (message: ChatMessage) => void;
  onEdit: (message: ChatMessage) => void;
  onData: () => void;
  onAnswer: (answer: string) => void;
  onFeedback: (id: string, value: 'up' | 'down') => void;
}

const isWebImage = (value: unknown): value is string =>
  typeof value === 'string' && /^https?:\/\//i.test(value);

export default function ResultPanel({
  messages,
  busy,
  onRetry,
  onRegenerate,
  onEdit,
  onData,
  onAnswer,
  onFeedback,
}: Props) {
  const [copyStatus, setCopyStatus] = useState('');

  const latest = [...messages]
    .reverse()
    .find(message => message.role === 'assistant')?.id;

  async function copy(message: ChatMessage) {
    try {
      await navigator.clipboard.writeText(
        message.content ||
          JSON.stringify(message.response?.result || {}, null, 2)
      );

      setCopyStatus('Copied');
    } catch {
      setCopyStatus('Copy unavailable; select the text and copy it.');
    }
  }

  return (
    <div className="conversation">
      <p className="copy-status" role="status">
        {copyStatus}
      </p>

      {messages.map(message => {
        const response = message.response;
        const result = response?.result;
        const metadata = response?.metadata;

        return (
          <article
            key={message.id}
            className={`message ${message.role}`}
          >
            {message.role === 'assistant' && (
              <div className="message-avatar">🛰️</div>
            )}

            <div className="message-content">
              <strong>
                {message.role === 'user' ? 'You' : 'SatQuery AI'}
              </strong>

              {message.fileName && (
                <div className="message-file">
                  📎 {message.fileName}
                </div>
              )}

              {message.role === 'assistant' && (
                <QueryStatus
                  response={response}
                  busy={busy && message.id === latest}
                  latest={message.id === latest}
                  stopped={message.stopped}
                  onRetry={() => onRetry(message)}
                  onData={onData}
                  onAnswer={onAnswer}
                />
              )}

              {message.notice && (
                <p className="integration-notice">
                  {message.notice}
                </p>
              )}

              {message.content && (
                <div className="chat-markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}

              {response && (
                <details className="query-details">
                  <summary>Query information</summary>

                  <dl>
                    <dt>Request</dt>
                    <dd>{response.request_id}</dd>

                    <dt>Intent / task</dt>
                    <dd>
                      {response.intent ||
                        response.task ||
                        'Not returned yet'}
                    </dd>

                    <dt>Inputs</dt>
                    <dd>
                      {response.inputs
                        ?.map(input => input.input_id)
                        .join(', ') || 'Not returned yet'}
                    </dd>

                    <dt>Modality</dt>
                    <dd>
                      {response.modality || 'Not returned yet'}
                    </dd>

                    <dt>Status</dt>
                    <dd>{response.status}</dd>
                  </dl>
                </details>
              )}

              {response?.status === 'COMPLETED' && (
                <>
                  {isWebImage(result?.image_url) && (
                    <img
                      className="message-image"
                      src={result.image_url}
                      alt="Analysis result"
                    />
                  )}

                  {result && (
                    <details className="query-details">
                      <summary>Structured result</summary>
                      <pre>
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </details>
                  )}

                  {typeof metadata?.confidence === 'number' && (
                    <p>
                      Confidence:{' '}
                      {(metadata.confidence * 100).toFixed(1)}%
                    </p>
                  )}

                  {typeof metadata?.processing_ms === 'number' && (
                    <p>
                      Processing: {metadata.processing_ms} ms
                    </p>
                  )}

                  {Array.isArray(metadata?.evidence) && (
                    <details className="query-details">
                      <summary>Evidence</summary>
                      <pre>
                        {JSON.stringify(metadata.evidence, null, 2)}
                      </pre>
                    </details>
                  )}

                  {response.spatial_output && (
                    <details className="query-details">
                      <summary>Spatial output</summary>
                      <pre>
                        {JSON.stringify(
                          response.spatial_output,
                          null,
                          2
                        )}
                      </pre>
                    </details>
                  )}
                </>
              )}

              {message.dataset && (
                <>
                  <DatasetInfo dataset={message.dataset} />
                  <MapView
                    dataset={message.dataset}
                    demoMode={false}
                  />
                </>
              )}

              <div className="message-actions">
                <button
                  className="message-action"
                  onClick={() => void copy(message)}
                >
                  Copy
                </button>

                {message.role === 'user' && (
                  <button
                    className="message-action"
                    disabled={busy}
                    onClick={() => onEdit(message)}
                  >
                    Edit
                  </button>
                )}

                {response?.status === 'COMPLETED' && (
                  <>
                    <button
                      className="message-action"
                      disabled={busy || message.id !== latest}
                      onClick={() => onRegenerate(message)}
                    >
                      Regenerate
                    </button>

                    <button
                      className="message-action"
                      aria-pressed={message.feedback === 'up'}
                      onClick={() =>
                        onFeedback(message.id, 'up')
                      }
                    >
                      Helpful
                    </button>

                    <button
                      className="message-action"
                      aria-pressed={message.feedback === 'down'}
                      onClick={() =>
                        onFeedback(message.id, 'down')
                      }
                    >
                      Not helpful
                    </button>
                  </>
                )}
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}