import { z } from "zod";
export const ChatMessageSchema = z.object({
    role: z.enum(["user", "assistant"]),
    content: z.string(),
});
export const ToolCallTraceSchema = z.object({
    name: z.string(),
    arguments: z.record(z.unknown()),
    result_preview: z.string(),
});
export const ChatResponseSchema = z.object({
    reply: z.string(),
    tool_calls: z.array(ToolCallTraceSchema),
    stop_reason: z.string(),
    iterations: z.number(),
});
