import axios, { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '',
});

// Request interceptor to add Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// TypeScript interfaces for request and response types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
}

export interface CreateSessionRequest {
  title: string;
}

export interface CreateSessionResponse {
  id: string;
  title: string;
  createdAt: string;
}

export interface File {
  id: string;
  source: string;
  createdAt: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface CreateMessageRequest {
  role: 'user' | 'assistant';
  content: string;
}

export interface CreateMessageResponse {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface IngestRequest {
  sessionId: string;
  files: File[];
}

export interface QueryRequest {
  sessionId: string;
  query: string;
}

// API client functions
export const createSession = (data: CreateSessionRequest) => api.post<CreateSessionResponse>('/api/sessions', data);

export const listSessions = () => api.get<CreateSessionResponse[]>('/api/sessions');

export const getSession = (sessionId: string) => api.get<CreateSessionResponse>(`/api/sessions/${sessionId}`);

export const uploadFile = (sessionId: string, file: File) =>
  api.post<File>(`/api/sessions/${sessionId}/files`, file);

export const listFiles = (sessionId: string) => api.get<File[]>(`/api/sessions/${sessionId}/files`);

export const getSessionMessages = (sessionId: string) =>
  api.get<Message[]>(`/api/sessions/${sessionId}/messages`);

export const createMessage = (sessionId: string, data: CreateMessageRequest) =>
  api.post<CreateMessageResponse>(`/api/sessions/${sessionId}/messages`, data);

export const ingestDocuments = (data: IngestRequest) => api.post('/api/ai/ingest', data);

export const aiQuery = (data: QueryRequest) => api.post('/api/ai/query', data);