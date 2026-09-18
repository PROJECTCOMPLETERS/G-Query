import { z } from "zod";
import type { Dataset } from "./dataset";

export const querySchema = z
  .object({
    request_id: z.string().min(1),

    status: z
      .string()
      .transform((status) => status.toUpperCase())
      .pipe(
        z.enum([
          "READY",
          "NEEDS_CLARIFICATION",
          "WAITING_FOR_DATA",
          "NOT_READY",
          "EXECUTING",
          "COMPLETED",
          "FAILED",
          "UNSUPPORTED",

          // Existing backend lifecycle states.
          "RECEIVED",
          "VALIDATING",
          "TASK_IDENTIFIED",
          "REQUIREMENTS_CHECKED",
          "EXECUTION_PLANNED",
        ])
      ),

    intent: z.string().optional(),
    modality: z.string().nullable().optional(),

    inputs: z
      .array(
        z.object({
          input_id: z.string(),
          type: z.string(),
        })
      )
      .optional(),

    question: z.string().optional(),
    options: z.array(z.string()).optional(),
    reason: z.string().optional(),

    missing_information: z.array(z.string()).optional(),
    available_observations: z.array(z.string()).optional(),

    error: z
      .object({
        code: z.string(),
        message: z.string(),
        stage: z.string(),
        recoverable: z.boolean(),
      })
      .optional(),

    task: z.string().optional(),
    result: z.record(z.unknown()).optional(),
    spatial_output: z.record(z.unknown()).nullable().optional(),
    metadata: z.record(z.unknown()).optional(),
  })
  .superRefine((value, context) => {
    if (value.status === "FAILED" && !value.error) {
      context.addIssue({
        code: "custom",
        message: "Missing structured error",
      });
    }
  });

export type QueryResponse = z.infer<typeof querySchema>;

export interface QueryInput {
  request_id: string;
  question: string;

  inputs: {
    input_id: string;
    type: "image";
  }[];

  modality?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;

  fileName?: string;
  dataset?: Dataset;

  response?: QueryResponse;
  input?: QueryInput;

  notice?: string;
  stopped?: boolean;
  feedback?: "up" | "down";
}

export interface Chat {
  id: string;
  title: string;
  updated: number;
  pinned: boolean;

  messages: ChatMessage[];
  dataset?: Dataset;
  observationIds: string[];
}