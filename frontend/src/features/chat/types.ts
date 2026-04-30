import { z } from "zod";

export const ChatMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
});
export type ChatMessage = z.infer<typeof ChatMessageSchema>;

export const ToolCallTraceSchema = z.object({
  name: z.string(),
  arguments: z.record(z.unknown()),
  result_preview: z.string(),
});
export type ToolCallTrace = z.infer<typeof ToolCallTraceSchema>;

export const ChatResponseSchema = z.object({
  reply: z.string(),
  tool_calls: z.array(ToolCallTraceSchema),
  stop_reason: z.string(),
  iterations: z.number(),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
