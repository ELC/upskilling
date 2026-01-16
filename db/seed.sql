-- Seed data aligned to the screens in the UpSkills PDF

INSERT INTO users (user_id, full_name, email, role, bio, created_at) VALUES
  (1, 'Priya Admin', 'priya.admin@upskills.local', 'admin', 'Platform administrator.', '2025-01-01 09:00:00'),
  (2, 'Ava Mentor', 'ava.mentor@upskills.local', 'mentor', 'Mentor for UX and product tracks.', '2025-01-01 09:05:00'),
  (3, 'Marco Mentor', 'marco.mentor@upskills.local', 'mentor', 'Mentor for frontend and data tracks.', '2025-01-01 09:10:00'),
  (4, 'John Smith', 'john.smith@upskills.local', 'mentee', 'Junior UX/UI Designer mentee.', '2025-01-10 10:00:00'),
  (5, 'Sara Lee', 'sara.lee@upskills.local', 'mentee', 'Frontend developer mentee.', '2025-01-10 10:05:00'),
  (6, 'Luis Perez', 'luis.perez@upskills.local', 'mentee', 'Frontend developer mentee.', '2025-01-15 11:00:00'),
  (7, 'Pat PathCreator', 'pat.pathcreator@upskills.local', 'path_creator', 'Builds career paths and content.', '2025-01-20 09:00:00');

INSERT INTO roles (role_id, name, description, max_active_paths) VALUES
  (1, 'admin', 'Full system administration.', NULL),
  (2, 'path_creator', 'Creates career paths and adds content.', NULL),
  (3, 'mentor', 'Assigns paths, validates steps, and provides feedback.', NULL),
  (4, 'mentee', 'Assigned to paths and tracks progress.', 3);

INSERT INTO actions (action_id, action_key, description) VALUES
  (1, 'team.view', 'View teams and members.'),
  (2, 'team.manage', 'Create and update teams.'),
  (3, 'career.create', 'Create a career track.'),
  (4, 'career.update', 'Edit a career track.'),
  (5, 'path_template.create', 'Create a learning path template.'),
  (6, 'path_template.update', 'Edit a learning path template.'),
  (7, 'path_content.add', 'Add content to a learning path.'),
  (8, 'paths.assign', 'Assign career paths to users.'),
  (9, 'paths.validate', 'Approve or reject path steps.'),
  (10, 'feedback.create', 'Create feedback for a mentee.'),
  (11, 'feedback.view', 'View feedback for a mentee.'),
  (12, 'paths.view', 'View available learning paths.'),
  (13, 'logbook.create', 'Create logbook entries.'),
  (14, 'logbook.view', 'View logbook entries.'),
  (15, 'progress.view', 'View progress dashboards.');

INSERT INTO role_actions (role_id, action_id) VALUES
  (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
  (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
  (1, 11), (1, 12), (1, 13), (1, 14), (1, 15),
  (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 12),
  (3, 1), (3, 8), (3, 9), (3, 10), (3, 11),
  (3, 12), (3, 13), (3, 14), (3, 15),
  (4, 12), (4, 11), (4, 13), (4, 14), (4, 15);

INSERT INTO teams (team_id, name, manager_user_id) VALUES
  (1, 'UX Team A', 2),
  (2, 'Frontend Team B', 3),
  (3, 'Product Team C', 2),
  (4, 'Data Team D', 3),
  (5, 'Growth Team E', 2);

INSERT INTO team_members (team_id, user_id) VALUES
  (1, 2),
  (1, 4),
  (1, 5),
  (2, 3),
  (2, 6),
  (3, 2),
  (4, 3),
  (5, 5);

INSERT INTO careers (career_id, name, specialization) VALUES
  (1, 'Frontend Developer', 'Web Applications'),
  (2, 'UX/UI Designer', 'UX Research'),
  (3, 'Backend Developer', 'API Engineering'),
  (4, 'Data Analyst', 'Business Intelligence'),
  (5, 'Product Manager', 'Growth');

INSERT INTO seniorities (seniority_id, name, rank) VALUES
  (1, 'Intern', 1),
  (2, 'Junior', 2),
  (3, 'Semi Senior', 3),
  (4, 'Senior', 4),
  (5, 'Lead', 5);

INSERT INTO path_templates (
  path_template_id,
  career_id,
  seniority_id,
  name,
  description,
  duration_hours,
  default_start_offset_days,
  default_deadline_offset_days,
  course_link
) VALUES
  (1, 1, 2, 'HTML & CSS Fundamentals',
    'Learn the basics of HTML structure and CSS styling.',
    40, 0, 45, 'https://learn.pwc.com/courses/html-css-fundamentals'),
  (2, 1, 2, 'JavaScript Basics',
    'Introduction to JavaScript programming fundamentals.',
    50, 46, 90, 'https://learn.pwc.com/courses/javascript-basics'),
  (3, 1, 3, 'React Development',
    'Build modern web applications with React.',
    60, 91, 150, 'https://learn.pwc.com/courses/react-development'),
  (4, 1, 4, 'Advanced Frontend Architecture',
    'Design scalable frontend architectures and patterns.',
    70, 151, 210, 'https://learn.pwc.com/courses/frontend-architecture'),
  (5, 2, 2, 'User Research Fundamentals',
    'Learn to conduct user interviews, surveys, and usability studies.',
    40, 0, 31, 'https://learn.pwc.com/courses/user-research-fundamentals'),
  (6, 2, 2, 'Design Thinking & User-Centered Design',
    'Master design thinking methodology and user-centered design principles.',
    50, 32, 70, 'https://learn.pwc.com/courses/design-thinking'),
  (7, 2, 2, 'Prototyping & Wireframing',
    'Learn to create wireframes and prototypes using design tools.',
    50, 71, 110, 'https://learn.pwc.com/courses/prototyping-wireframing'),
  (8, 2, 3, 'Final Project',
    'Complete the final project for this career path.',
    60, 111, 150, NULL);

INSERT INTO path_template_steps (
  step_id,
  path_template_id,
  step_order,
  name,
  description,
  duration_hours
) VALUES
  (1, 5, 1, 'Research planning',
    'Define research goals, participant criteria, and methodology.', 6),
  (2, 5, 2, 'Interview guide',
    'Prepare interview questions and consent workflow.', 6),
  (3, 5, 3, 'Conduct interviews',
    'Run interviews and collect qualitative data.', 14),
  (4, 5, 4, 'Synthesize insights',
    'Cluster findings and write a summary.', 8),
  (5, 6, 1, 'Empathy mapping',
    'Build empathy maps from prior research.', 6),
  (6, 6, 2, 'Problem framing',
    'Define problem statements and assumptions.', 8),
  (7, 6, 3, 'Ideation workshop',
    'Facilitate ideation and prioritize concepts.', 10),
  (8, 7, 1, 'Wireframe basics',
    'Create low-fidelity wireframes for key flows.', 8),
  (9, 7, 2, 'Prototype flows',
    'Build interactive prototypes for testing.', 12),
  (10, 7, 3, 'Usability test',
    'Run usability tests and capture issues.', 10),
  (11, 1, 1, 'HTML foundations',
    'Learn semantic structure and accessibility basics.', 12),
  (12, 1, 2, 'CSS layout',
    'Practice flexbox, grid, and responsive design.', 12),
  (13, 1, 3, 'Component styling',
    'Style reusable components and pages.', 12),
  (14, 2, 1, 'JS fundamentals',
    'Variables, functions, and control flow.', 16),
  (15, 2, 2, 'DOM basics',
    'Manipulate DOM and handle events.', 16),
  (16, 2, 3, 'Async patterns',
    'Promises, async/await, and fetch.', 16);

INSERT INTO path_step_dependencies (step_id, depends_on_step_id) VALUES
  (2, 1),
  (3, 2),
  (4, 3),
  (6, 5),
  (7, 6),
  (9, 8),
  (10, 9),
  (12, 11),
  (13, 12),
  (15, 14),
  (16, 15);

INSERT INTO path_template_dependencies (path_template_id, depends_on_path_template_id) VALUES
  (2, 1),
  (3, 2),
  (4, 3),
  (6, 5),
  (7, 6),
  (8, 7);

INSERT INTO user_career_paths (
  user_career_path_id,
  user_id,
  career_id,
  start_date,
  deadline,
  overall_progress_percent
) VALUES
  (1, 4, 2, '2025-01-14', '2025-06-14', 75),
  (2, 5, 1, '2025-01-10', '2025-07-01', 45),
  (3, 6, 1, '2025-02-01', '2025-08-01', 20),
  (4, 4, 1, '2025-03-01', '2025-09-01', 10),
  (5, 5, 5, '2025-01-20', '2025-05-20', 5);

INSERT INTO user_path_assignments (
  user_path_assignment_id,
  user_career_path_id,
  path_template_id,
  start_date,
  deadline,
  status,
  progress_percent,
  mentor_validation_status
) VALUES
  (1, 1, 5, '2025-01-14', '2025-02-14', 'Completed', 100, 'Approved'),
  (2, 1, 6, '2025-02-15', '2025-03-15', 'Completed', 100, 'Approved'),
  (3, 1, 7, '2025-03-16', '2025-04-16', 'Completed', 100, 'Pending'),
  (4, 1, 8, '2025-04-17', '2025-06-14', 'Pending', 0, 'Pending'),
  (5, 2, 1, '2025-01-10', '2025-02-14', 'Completed', 100, 'Approved'),
  (6, 2, 2, '2025-02-15', '2025-03-31', 'In Progress', 60, 'Pending'),
  (7, 2, 3, '2025-04-01', '2025-05-31', 'Pending', 0, 'Pending'),
  (8, 3, 1, '2025-02-01', '2025-03-15', 'In Progress', 40, 'Pending'),
  (9, 3, 2, '2025-03-16', '2025-04-30', 'Pending', 0, 'Pending'),
  (10, 4, 1, '2025-03-01', '2025-04-10', 'Pending', 0, 'Pending');

INSERT INTO user_step_progress (
  user_step_progress_id,
  user_path_assignment_id,
  step_id,
  status,
  progress_percent,
  updated_at
) VALUES
  (1, 1, 1, 'Completed', 100, '2025-01-20 10:00:00'),
  (2, 1, 2, 'Completed', 100, '2025-01-28 10:00:00'),
  (3, 1, 3, 'Completed', 100, '2025-02-08 10:00:00'),
  (4, 1, 4, 'Completed', 100, '2025-02-13 10:00:00'),
  (5, 2, 5, 'Completed', 100, '2025-02-20 10:00:00'),
  (6, 2, 6, 'Completed', 100, '2025-03-01 10:00:00'),
  (7, 2, 7, 'Completed', 100, '2025-03-10 10:00:00'),
  (8, 3, 8, 'Completed', 100, '2025-03-20 10:00:00'),
  (9, 3, 9, 'In Progress', 60, '2025-04-05 10:00:00'),
  (10, 3, 10, 'Pending', 0, '2025-04-10 10:00:00'),
  (11, 5, 11, 'Completed', 100, '2025-01-20 10:00:00'),
  (12, 5, 12, 'Completed', 100, '2025-02-01 10:00:00'),
  (13, 5, 13, 'Completed', 100, '2025-02-10 10:00:00'),
  (14, 6, 14, 'In Progress', 70, '2025-03-05 10:00:00'),
  (15, 6, 15, 'In Progress', 40, '2025-03-20 10:00:00'),
  (16, 6, 16, 'Pending', 0, '2025-03-28 10:00:00');

INSERT INTO log_entries (
  log_entry_id,
  user_id,
  user_career_path_id,
  entry_type,
  entry_date,
  notes,
  related_user_path_assignment_id
) VALUES
  (1, 4, 1, 'Meeting/Conversation', '2025-02-09',
    'Discussed progress on User Research Fundamentals and next steps.', 1),
  (2, 4, 1, 'Path Approved', '2025-02-11',
    'Approved User Research Fundamentals course. Strong survey design skills.', 1),
  (3, 4, 1, 'Path Approved', '2025-03-16',
    'Approved Design Thinking & User-Centered Design path.', 2),
  (4, 4, 1, 'General', '2025-04-10',
    'Reviewed wireframe deliverables and feedback summary.', 3),
  (5, 5, 2, 'Meeting/Conversation', '2025-03-01',
    'Checked in on JavaScript Basics progress and blockers.', 6),
  (6, 6, 3, 'Meeting/Conversation', '2025-02-20',
    'Kickoff meeting for HTML & CSS Fundamentals.', 8),
  (7, 5, 5, 'General', '2025-02-01',
    'Initial product discovery notes logged.', NULL),
  (8, 4, 4, 'General', '2025-03-05',
    'Started frontend ramp-up for supplemental learning.', 10);

