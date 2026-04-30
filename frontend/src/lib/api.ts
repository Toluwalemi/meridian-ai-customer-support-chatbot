import axios, { AxiosInstance } from "axios";
import { env } from "./env";

export function createApiClient(getToken: () => Promise<string | null>): AxiosInstance {
  const instance = axios.create({
    baseURL: env.VITE_API_URL,
    timeout: 60_000,
  });

  instance.interceptors.request.use(async (config) => {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  return instance;
}
