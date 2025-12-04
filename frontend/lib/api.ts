import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"];
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  register: async (data: { username: string; email: string; password: string; password2: string }) => {
    const response = await api.post("/api/auth/register/", data);
    return response.data;
  },
  login: async (data: { email: string; password: string }) => {
    const response = await api.post("/api/auth/login/", data);
    return response.data;
  },
};

export const transactionsAPI = {
  list: async (params?: {
    start_date?: string;
    end_date?: string;
    type?: string;
    currency?: string;
    category?: string;
    target_currency?: string;
    page?: number;
  }) => {
    const response = await api.get("/api/transactions/", { params });
    return response.data;
  },
  get: async (id: number, target_currency?: string) => {
    const response = await api.get(`/api/transactions/${id}/`, {
      params: target_currency ? { target_currency } : {},
    });
    return response.data;
  },
  upload: async (file: File, idempotencyKey?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }
    const response = await api.post("/api/transactions/upload/", formData, {
      headers,
    });
    return response.data;
  },
};

export const reportsAPI = {
  summary: async (params: {
    start_date: string;
    end_date: string;
    target_currency?: string;
  }) => {
    const response = await api.get("/api/reports/summary/", { params });
    return response.data;
  },
  convertCurrency: async (params: {
    amount: number;
    from_currency: string;
    to_currency: string;
    date?: string;
  }) => {
    const response = await api.get("/api/reports/convert-currency/", { params });
    return response.data;
  },
};

