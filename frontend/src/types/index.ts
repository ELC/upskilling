// User types
export interface Role {
  role_id: number;
  name: string;
  description: string | null;
  max_active_paths: number | null;
}

export interface User {
  user_id: number;
  full_name: string;
  email: string;
  bio: string | null;
  created_at: string;
  roles: Role[];
}

export interface UserWithPermissions extends User {
  permissions: string[];
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  bio?: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

// Team types
export interface Team {
  team_id: number;
  name: string;
  manager_user_id: number;
}

export interface TeamMember {
  user_id: number;
  full_name: string;
  email: string;
}

export interface TeamWithMembers extends Team {
  manager: User;
  members: TeamMember[];
}

export interface TeamListItem {
  team_id: number;
  name: string;
  member_count: number;
  manager_name: string;
}

// Career types
export interface Career {
  career_id: number;
  name: string;
  specialization: string | null;
}

export interface CareerWithPaths extends Career {
  path_templates: PathTemplate[];
}

// Path types
export interface PathTemplate {
  path_template_id: number;
  career_id: number;
  name: string;
  description: string;
  duration_hours: number;
  default_start_offset_days: number | null;
  default_deadline_offset_days: number | null;
}

export interface PathStepDependency {
  depends_on_step_id: number;
  depends_on_step_name: string;
}

export interface PathStep {
  step_id: number;
  path_template_id: number;
  step_order: number;
  name: string;
  description: string | null;
  duration_hours: number | null;
  course_link: string | null;
  dependencies: PathStepDependency[];
}

export interface PathTemplateWithSteps extends PathTemplate {
  steps: PathStep[];
}

// Progress types
export interface UserCareerPath {
  user_career_path_id: number;
  user_id: number;
  career_id: number;
  start_date: string;
  end_date: string;
  overall_progress_percent: number;
}

export interface UserCareerPathDetail extends UserCareerPath {
  career_name: string;
  career_specialization: string | null;
  path_assignments: UserPathAssignment[];
}

export interface UserPathAssignment {
  user_path_assignment_id: number;
  user_career_path_id: number;
  path_template_id: number;
  start_date: string;
  deadline: string;
  status: 'Pending' | 'In Progress' | 'Completed';
  progress_percent: number;
  mentor_validation_status: 'Pending' | 'Approved' | 'Rejected';
}

export interface UserPathAssignmentDetail extends UserPathAssignment {
  path_template: PathTemplate;
  step_progress: UserStepProgress[];
}

export interface UserStepProgress {
  user_step_progress_id: number;
  user_path_assignment_id: number;
  step_id: number;
  status: 'Pending' | 'In Progress' | 'Completed';
  progress_percent: number;
  planned_start_date: string | null;
  planned_end_date: string | null;
  actual_start_date: string | null;
  actual_end_date: string | null;
  updated_at: string;
  step: PathStep | null;
}

export interface DashboardStats {
  current_career: string | null;
  current_path: string | null;
  current_path_progress: number;
  paths_remaining: number;
  overall_progress: number;
  skills_obtained: number;
}

export interface MenteeProgressSummary {
  user_id: number;
  full_name: string;
  email: string;
  career_name: string;
  start_date: string;
  end_date: string;
  overall_progress_percent: number;
  paths_completed: number;
  paths_total: number;
  pending_validation: number;
}

// Log entry types
export interface LogEntry {
  log_entry_id: number;
  user_id: number;
  user_career_path_id: number;
  entry_type: string;
  entry_date: string;
  notes: string;
  related_user_path_assignment_id: number | null;
}

export interface LogEntryDetail extends LogEntry {
  user_name: string;
  path_name: string | null;
}

// API response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MessageResponse {
  message: string;
  detail?: string;
}
