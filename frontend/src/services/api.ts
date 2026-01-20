import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  UserWithPermissions,
  Team,
  TeamWithMembers,
  TeamListItem,
  Career,
  CareerWithPaths,
  PathTemplate,
  PathTemplateWithSteps,
  PathStep,
  UserCareerPath,
  UserCareerPathDetail,
  UserPathAssignment,
  UserPathAssignmentDetail,
  UserStepProgress,
  DashboardStats,
  MenteeProgressSummary,
  LogEntry,
  LogEntryDetail,
  PaginatedResponse,
  MessageResponse,
} from '../types';

const API_BASE_URL = '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post<TokenResponse>(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        }
      } catch {
        // Refresh failed, clear tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },
  
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },
  
  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
  
  me: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
  
  requestPasswordReset: async (email: string): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/auth/password-reset-request', { email });
    return response.data;
  },
  
  resetPassword: async (token: string, newPassword: string): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/auth/password-reset', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },
};

// Users API
export const usersApi = {
  getMe: async (): Promise<UserWithPermissions> => {
    const response = await api.get<UserWithPermissions>('/users/me');
    return response.data;
  },
  
  updateMe: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  },
  
  changePassword: async (currentPassword: string, newPassword: string): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
  
  list: async (page = 1, pageSize = 20): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/users', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  
  get: async (userId: number): Promise<User> => {
    const response = await api.get<User>(`/users/${userId}`);
    return response.data;
  },
};

// Teams API
export const teamsApi = {
  list: async (page = 1, pageSize = 20): Promise<PaginatedResponse<TeamListItem>> => {
    const response = await api.get<PaginatedResponse<TeamListItem>>('/teams', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  
  getMyTeams: async (): Promise<TeamWithMembers[]> => {
    const response = await api.get<TeamWithMembers[]>('/teams/my-teams');
    return response.data;
  },
  
  get: async (teamId: number): Promise<TeamWithMembers> => {
    const response = await api.get<TeamWithMembers>(`/teams/${teamId}`);
    return response.data;
  },
  
  create: async (data: { name: string; manager_user_id: number }): Promise<TeamWithMembers> => {
    const response = await api.post<TeamWithMembers>('/teams', data);
    return response.data;
  },
  
  update: async (teamId: number, data: Partial<Team>): Promise<TeamWithMembers> => {
    const response = await api.put<TeamWithMembers>(`/teams/${teamId}`, data);
    return response.data;
  },
  
  addMember: async (teamId: number, userId: number): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>(`/teams/${teamId}/members`, { user_id: userId });
    return response.data;
  },
  
  removeMember: async (teamId: number, userId: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/teams/${teamId}/members/${userId}`);
    return response.data;
  },
};

// Careers API
export const careersApi = {
  list: async (page = 1, pageSize = 20): Promise<PaginatedResponse<Career>> => {
    const response = await api.get<PaginatedResponse<Career>>('/careers', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  
  get: async (careerId: number): Promise<CareerWithPaths> => {
    const response = await api.get<CareerWithPaths>(`/careers/${careerId}`);
    return response.data;
  },
  
  create: async (data: { name: string; specialization?: string }): Promise<Career> => {
    const response = await api.post<Career>('/careers', data);
    return response.data;
  },
};

// Paths API
export const pathsApi = {
  list: async (page = 1, pageSize = 20, careerId?: number): Promise<PaginatedResponse<PathTemplate>> => {
    const response = await api.get<PaginatedResponse<PathTemplate>>('/paths', {
      params: { page, page_size: pageSize, career_id: careerId },
    });
    return response.data;
  },
  
  get: async (pathId: number): Promise<PathTemplateWithSteps> => {
    const response = await api.get<PathTemplateWithSteps>(`/paths/${pathId}`);
    return response.data;
  },
  
  create: async (data: Partial<PathTemplate>): Promise<PathTemplate> => {
    const response = await api.post<PathTemplate>('/paths', data);
    return response.data;
  },
  
  getSteps: async (pathId: number): Promise<PathStep[]> => {
    const response = await api.get<PathStep[]>(`/paths/${pathId}/steps`);
    return response.data;
  },
  
  createStep: async (pathId: number, data: Partial<PathStep>): Promise<PathStep> => {
    const response = await api.post<PathStep>(`/paths/${pathId}/steps`, data);
    return response.data;
  },
};

// Progress API
export const progressApi = {
  getDashboard: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/progress/dashboard');
    return response.data;
  },
  
  getCareerPaths: async (): Promise<UserCareerPathDetail[]> => {
    const response = await api.get<UserCareerPathDetail[]>('/progress/career-paths');
    return response.data;
  },
  
  getCareerPath: async (careerPathId: number): Promise<UserCareerPathDetail> => {
    const response = await api.get<UserCareerPathDetail>(`/progress/career-paths/${careerPathId}`);
    return response.data;
  },
  
  assignCareerPath: async (data: {
    user_id: number;
    career_id: number;
    start_date: string;
    end_date: string;
  }): Promise<UserCareerPath> => {
    const response = await api.post<UserCareerPath>('/progress/career-paths', data);
    return response.data;
  },
  
  getAssignment: async (assignmentId: number): Promise<UserPathAssignmentDetail> => {
    const response = await api.get<UserPathAssignmentDetail>(`/progress/assignments/${assignmentId}`);
    return response.data;
  },
  
  assignPath: async (data: {
    user_career_path_id: number;
    path_template_id: number;
    start_date: string;
    deadline: string;
  }): Promise<UserPathAssignment> => {
    const response = await api.post<UserPathAssignment>('/progress/assignments', data);
    return response.data;
  },
  
  updateAssignment: async (assignmentId: number, data: Partial<UserPathAssignment>): Promise<UserPathAssignment> => {
    const response = await api.put<UserPathAssignment>(`/progress/assignments/${assignmentId}`, data);
    return response.data;
  },
  
  getStepProgress: async (assignmentId: number): Promise<UserStepProgress[]> => {
    const response = await api.get<UserStepProgress[]>(`/progress/assignments/${assignmentId}/steps`);
    return response.data;
  },
  
  updateStepProgress: async (progressId: number, data: Partial<UserStepProgress>): Promise<UserStepProgress> => {
    const response = await api.put<UserStepProgress>(`/progress/steps/${progressId}`, data);
    return response.data;
  },
  
  getPendingValidations: async (): Promise<UserPathAssignmentDetail[]> => {
    const response = await api.get<UserPathAssignmentDetail[]>('/progress/pending-validations');
    return response.data;
  },
  
  approveAssignment: async (assignmentId: number): Promise<UserPathAssignment> => {
    const response = await api.post<UserPathAssignment>(`/progress/assignments/${assignmentId}/approve`);
    return response.data;
  },
  
  rejectAssignment: async (assignmentId: number): Promise<UserPathAssignment> => {
    const response = await api.post<UserPathAssignment>(`/progress/assignments/${assignmentId}/reject`);
    return response.data;
  },
  
  getTeamProgress: async (): Promise<MenteeProgressSummary[]> => {
    const response = await api.get<MenteeProgressSummary[]>('/progress/team-progress');
    return response.data;
  },
};

// Logbook API
export const logbookApi = {
  getEntries: async (careerPathId: number): Promise<LogEntryDetail[]> => {
    const response = await api.get<LogEntryDetail[]>(`/logbook/career-path/${careerPathId}`);
    return response.data;
  },
  
  createEntry: async (data: Partial<LogEntry>): Promise<LogEntry> => {
    const response = await api.post<LogEntry>('/logbook', data);
    return response.data;
  },
  
  updateEntry: async (entryId: number, data: Partial<LogEntry>): Promise<LogEntry> => {
    const response = await api.put<LogEntry>(`/logbook/${entryId}`, data);
    return response.data;
  },
  
  deleteEntry: async (entryId: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/logbook/${entryId}`);
    return response.data;
  },
};

export default api;
