import { z } from "zod";
const schema = z.object({
    VITE_API_URL: z.string().url(),
    VITE_APP_NAME: z.string().default("Meridian Support"),
    VITE_CLERK_PUBLISHABLE_KEY: z.string().optional(),
});
export const env = schema.parse(import.meta.env);
export function hasValidClerkPublishableKey(key) {
    if (!key) {
        return false;
    }
    return key.startsWith("pk_") && !key.includes("...");
}
