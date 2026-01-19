# UpSkills

A career development and upskilling platform that enables organizations to manage learning paths, track employee progress, and facilitate mentor-mentee relationships.

## Overview

UpSkills helps organizations:

- **Define Career Paths**: Create structured learning journeys with courses, steps, and dependencies
- **Assign & Track Progress**: Mentors assign paths to mentees and monitor completion
- **Validate Learning**: Mentors approve/reject completed steps and provide feedback via logbook entries
- **Manage Teams**: Organize users into teams with managers overseeing progress

## Roles

| Role | Responsibilities |
|------|------------------|
| **Admin** | Full system access - manage users, roles, careers, paths, and all settings |
| **Path Creator** | Create and edit career paths, define steps and dependencies, manage content |
| **Mentor** | Assign paths to mentees, validate progress, approve/reject steps, add logbook feedback |
| **Mentee** | View assigned paths, track progress, mark steps complete (pending validation) |

## Tech Stack

- **Frontend**: React
- **Backend**: .NET 10
- **Database**: Relational (SQL)

## Database Schema

```mermaid
erDiagram
    users {
        int user_id PK
        string full_name
        string email
        string bio
        timestamp created_at
    }

    roles {
        int role_id PK
        string name
        string description
        int max_active_paths
    }

    actions {
        int action_id PK
        string action_key
        string description
    }

    role_actions {
        int role_id FK
        int action_id FK
    }

    user_roles {
        int user_id FK
        int role_id FK
    }

    teams {
        int team_id PK
        string name
        int manager_user_id FK
    }

    team_members {
        int team_id FK
        int user_id FK
    }

    careers {
        int career_id PK
        string name
        string specialization
    }

    path_templates {
        int path_template_id PK
        int career_id FK
        string name
        string description
        int duration_hours
    }

    path_template_steps {
        int step_id PK
        int path_template_id FK
        int step_order
        string name
        string description
        int duration_hours
        string course_link
    }

    path_step_dependencies {
        int step_id FK
        int depends_on_step_id FK
    }

    user_career_paths {
        int user_career_path_id PK
        int user_id FK
        int career_id FK
        date start_date
        date end_date
        int overall_progress_percent
    }

    user_path_assignments {
        int user_path_assignment_id PK
        int user_career_path_id FK
        int path_template_id FK
        date start_date
        date deadline
        string status
        int progress_percent
        string mentor_validation_status
    }

    user_step_progress {
        int user_step_progress_id PK
        int user_path_assignment_id FK
        int step_id FK
        string status
        int progress_percent
        date planned_start_date
        date planned_end_date
        date actual_start_date
        date actual_end_date
        timestamp updated_at
    }

    log_entries {
        int log_entry_id PK
        int user_id FK
        int user_career_path_id FK
        string entry_type
        date entry_date
        string notes
        int related_user_path_assignment_id FK
    }

    %% Relationships
    roles ||--o{ role_actions : has
    actions ||--o{ role_actions : granted_to
    users ||--o{ user_roles : has
    roles ||--o{ user_roles : assigned_to

    users ||--o{ teams : manages
    teams ||--o{ team_members : contains

    careers ||--o{ path_templates : contains
    path_templates ||--o{ path_template_steps : has
    path_template_steps ||--o{ path_step_dependencies : depends_on

    users ||--o{ user_career_paths : assigned
    careers ||--o{ user_career_paths : defines
    user_career_paths ||--o{ user_path_assignments : includes
    path_templates ||--o{ user_path_assignments : instantiates
    user_path_assignments ||--o{ user_step_progress : tracks
    path_template_steps ||--o{ user_step_progress : references

    users ||--o{ log_entries : writes
    user_career_paths ||--o{ log_entries : about
    user_path_assignments ||--o{ log_entries : related_to
```

## Project Structure

```
upskilling/
├── db/
│   ├── schema.sql      # Database table definitions
│   └── seed.sql        # Demo data for development
├── docs/
│   └── db/
│       └── tables.md   # Quick reference for tables
└── README.md
```

## Getting Started

1. **Database Setup**
   ```bash
   # Run schema creation
   psql -d your_db -f db/schema.sql
   
   # Load demo data
   psql -d your_db -f db/seed.sql
   ```

2. **Backend** (coming soon)
3. **Frontend** (coming soon)

## License

Internal use only.
