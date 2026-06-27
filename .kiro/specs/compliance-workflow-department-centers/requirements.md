# Requirements Document

## Introduction

This document specifies requirements for Phase 2 of the RegIntel AI application: Compliance Workflow & Department Action Centers. The feature transforms the existing analytics dashboard into a realistic banking compliance workflow system while preserving the existing offline architecture and Phase 1 authentication mechanisms.

The core enhancement introduces a complete workflow lifecycle from RBI circular upload through AI processing, manual approval, department assignment, compliance execution, and head office verification. A critical addition is the approval step where Head Office reviews AI-generated department suggestions before publishing assignments.

## Glossary

- **System**: The RegIntel AI application (backend and frontend)
- **Head_Office_User**: A user with role "head_office" who can upload circulars, approve assignments, and verify completion
- **Department_User**: A user with role "department" assigned to a specific department who can view and update assigned work
- **RBI_Circular**: A PDF regulatory document uploaded by Head Office
- **Requirement**: An extracted compliance requirement from an RBI Circular
- **MAP**: Mitigation Action Plan - a compliance action plan for a requirement
- **Assignment**: A requirement assigned to a specific department
- **Assignment_Center**: A new page where Head Office reviews AI suggestions before publishing
- **AI_Suggestion**: AI-generated recommendation including department, confidence score, and reasoning
- **Department_Dashboard**: Department-specific view showing only assigned work
- **Knowledge_Graph**: Visual representation of relationships between circulars, requirements, MAPs, and departments
- **Department_Knowledge_Graph**: Scoped knowledge graph showing only data relevant to a specific department
- **Audit_Trail**: Complete timeline of all events and status changes for a task
- **Task_Status**: One of: Assigned, In_Progress, Completed, Verified
- **Priority_Level**: One of: Critical, High, Medium, Low
- **Approval_Action**: One of: Approve, Reassign, Reject
- **Real_Time_Update**: UI update without page refresh using polling mechanism
- **Export_Report**: Generated PDF document containing compliance information

## Requirements

### Requirement 1: Assignment Center Creation

**User Story:** As a Head Office user, I want to review AI suggestions in a dedicated Assignment Center before publishing them to departments, so that I can ensure proper task distribution and correct any AI misassignments.

#### Acceptance Criteria

1. WHEN a Head Office user navigates to the Assignment Center, THE System SHALL display all unassigned requirements with their AI suggestions
2. FOR each unassigned requirement, THE System SHALL display the requirement text, suggested department, confidence score (0-100%), AI reasoning, priority level, and suggested MAP
3. WHERE a Head Office user selects an Approve action, THE System SHALL create an assignment record with status "assigned" and make it visible to the target department
4. WHERE a Head Office user selects a Reassign action, THE System SHALL display a department selector and create an assignment to the manually selected department
5. WHERE a Head Office user selects a Reject action, THE System SHALL mark the requirement as not-to-be-assigned and exclude it from department views
6. THE Assignment_Center SHALL display action buttons (Approve, Reassign, Reject) for each requirement
7. WHEN a Head Office user approves multiple requirements, THE System SHALL process all approvals and update the Assignment Center display within 2 seconds

### Requirement 2: AI Suggestion Display

**User Story:** As a Head Office user, I want to see detailed AI suggestions with confidence scores and reasoning, so that I can make informed approval decisions.

#### Acceptance Criteria

1. FOR each AI suggestion, THE System SHALL display a confidence score between 0 and 100 percent
2. FOR each AI suggestion, THE System SHALL display textual reasoning explaining why the department was suggested
3. WHERE confidence score is below 60%, THE System SHALL highlight the suggestion with a warning indicator
4. THE System SHALL sort suggestions by confidence score in descending order by default
5. WHERE multiple departments have similar confidence scores (within 10%), THE System SHALL display all candidate departments with their respective scores
6. THE System SHALL display the suggested MAP title and description for each requirement
7. WHEN a Head Office user hovers over a confidence score, THE System SHALL display a tooltip with detailed scoring breakdown

### Requirement 3: Manual Assignment Override

**User Story:** As a Head Office user, I want to manually reassign requirements to different departments when AI suggestions are incorrect, so that work goes to the most appropriate team.

#### Acceptance Criteria

1. WHEN a Head Office user clicks Reassign, THE System SHALL display a dropdown list of all active departments
2. THE System SHALL allow selection of any department regardless of AI suggestion
3. WHEN a Head Office user confirms reassignment, THE System SHALL create an assignment to the selected department
4. THE System SHALL record the manual override in the audit trail with the reason "Manual Override by [username]"
5. WHEN a manual reassignment is made, THE System SHALL update the Assignment Center display within 1 second
6. THE System SHALL support bulk reassignment of multiple requirements to the same department
7. WHERE a department is selected that differs from AI suggestion, THE System SHALL display a confirmation dialog showing the confidence score difference

### Requirement 4: Department Access Restrictions

**User Story:** As a Department user, I want to see only work assigned to my department, so that I can focus on my responsibilities without information overload.

#### Acceptance Criteria

1. WHEN a Department user logs in, THE System SHALL restrict access to only department-scoped pages
2. THE System SHALL prevent Department users from accessing the Regulatory Intelligence Pipeline page
3. THE System SHALL prevent Department users from accessing the Executive Dashboard page
4. THE System SHALL prevent Department users from accessing the institution-wide Knowledge Graph
5. THE System SHALL prevent Department users from accessing global analytics views
6. WHERE a Department user attempts to access a restricted URL, THE System SHALL return HTTP 403 Forbidden
7. THE System SHALL redirect Department users to the Department Dashboard after login

### Requirement 5: Department Dashboard Creation

**User Story:** As a Department user, I want to see a dashboard showing my department's work metrics, so that I can track our compliance progress.

#### Acceptance Criteria

1. THE Department_Dashboard SHALL display task status counts: Assigned, In_Progress, Completed, Verified
2. THE Department_Dashboard SHALL display priority breakdown counts: Critical, High, Medium, Low
3. THE Department_Dashboard SHALL display a completion percentage calculated as (Completed + Verified) / Total * 100
4. THE Department_Dashboard SHALL display a list of the 10 most recent assignments ordered by assigned date descending
5. THE Department_Dashboard SHALL display upcoming deadlines within the next 30 days
6. THE Department_Dashboard SHALL provide filter controls for status and priority
7. WHEN a Department user applies a filter, THE System SHALL update the dashboard display within 500 milliseconds

### Requirement 6: Assigned Requirements View

**User Story:** As a Department user, I want to see a list of all requirements assigned to my department, so that I can review and manage our compliance obligations.

#### Acceptance Criteria

1. THE Assigned_Requirements view SHALL display all requirements assigned to the logged-in user's department
2. FOR each requirement, THE System SHALL display: requirement ID, title, source circular, priority, status, assigned date, deadline
3. THE System SHALL provide sorting by assigned date, deadline, priority, and status
4. THE System SHALL provide filtering by status and priority
5. THE System SHALL provide a search box that filters requirements by text content
6. WHEN a Department user clicks "View Details", THE System SHALL display the full requirement text, AI reasoning, and complete audit trail
7. THE System SHALL display action buttons "Update Status" for each requirement in Assigned or In_Progress status

### Requirement 7: Assigned MAPs View

**User Story:** As a Department user, I want to see all MAPs assigned to my department, so that I can track action plans for compliance.

#### Acceptance Criteria

1. THE Assigned_MAPs view SHALL display all MAPs assigned to the logged-in user's department
2. FOR each MAP, THE System SHALL display: MAP title, description, related requirement, status, priority
3. THE System SHALL link each MAP to its parent requirement
4. WHEN a Department user clicks a MAP, THE System SHALL display detailed MAP information including all action steps
5. THE System SHALL provide action buttons "Mark Progress" for each MAP
6. THE System SHALL allow Department users to add notes and progress updates to MAPs
7. THE System SHALL display the most recent progress update timestamp for each MAP

### Requirement 8: Department-Scoped Knowledge Graph

**User Story:** As a Department user, I want to see a knowledge graph showing only my department's work, so that I can understand relationships without seeing irrelevant data.

#### Acceptance Criteria

1. THE Department_Knowledge_Graph SHALL display only the following nodes: Circular, Assigned Requirements, Assigned MAPs, Current Department
2. THE System SHALL exclude all other departments and their assignments from the graph
3. THE System SHALL exclude unassigned requirements from the Department Knowledge Graph
4. WHEN a Department user clicks a node, THE System SHALL display node details in a side panel
5. WHEN a Department user hovers over a node, THE System SHALL display a tooltip with quick information
6. THE System SHALL use color coding to indicate status: green for Verified, yellow for Completed, orange for In_Progress, grey for Assigned
7. THE System SHALL provide filter controls for status and priority that update the graph in real-time

### Requirement 9: Task Status Lifecycle Management

**User Story:** As a Department user, I want to update task status as I work through compliance tasks, so that Head Office can track progress.

#### Acceptance Criteria

1. THE System SHALL support the following status transitions: Assigned → In_Progress, In_Progress → Completed
2. THE System SHALL allow Department users to update status from Assigned to In_Progress
3. THE System SHALL allow Department users to update status from In_Progress to Completed
4. THE System SHALL prevent Department users from setting status to Verified
5. WHEN a Department user updates status to Completed, THE System SHALL record completion timestamp
6. THE System SHALL require a remarks field when updating status to Completed
7. WHEN status is updated, THE System SHALL create a status history record with old status, new status, changed by, and timestamp

### Requirement 10: Head Office Verification

**User Story:** As a Head Office user, I want to verify completed work from departments, so that I can ensure compliance obligations are properly fulfilled.

#### Acceptance Criteria

1. THE System SHALL allow Head Office users to update assignment status from Completed to Verified
2. THE System SHALL prevent Head Office users from updating status to Verified if current status is not Completed
3. WHEN a Head Office user marks an assignment as Verified, THE System SHALL record verification timestamp and user ID
4. THE System SHALL display a list of assignments pending verification on the Head Office dashboard
5. THE System SHALL sort pending verifications by completion date ascending
6. WHEN verification is completed, THE System SHALL update all related dashboards within 2 seconds
7. THE System SHALL allow Head Office users to add verification notes or request rework by changing status back to In_Progress

### Requirement 11: Real-Time Dashboard Synchronization

**User Story:** As any user, I want to see dashboard updates automatically without refreshing the page, so that I always have current information.

#### Acceptance Criteria

1. WHEN a Department user updates task status, THE System SHALL update the Department Dashboard within 3 seconds without page refresh
2. WHEN a Department user updates task status, THE System SHALL update the Head Office Dashboard within 3 seconds without page refresh
3. THE System SHALL use polling with a 5-second interval to check for updates
4. WHEN an assignment status changes, THE System SHALL update executive metrics immediately
5. WHEN an assignment status changes, THE System SHALL update completion percentages on all affected dashboards
6. WHEN an assignment status changes, THE System SHALL update heatmaps with new status counts
7. WHEN an assignment status changes, THE System SHALL update knowledge graph node colors to reflect new status

### Requirement 12: Assignment Notifications

**User Story:** As a Department user, I want to be notified when new work is assigned to my department, so that I can respond promptly.

#### Acceptance Criteria

1. WHEN Head Office approves an assignment, THE System SHALL create a notification record for the target department
2. THE notification SHALL include: assignment ID, priority level, deadline, source circular, timestamp
3. THE System SHALL display a notification badge on the Department Dashboard showing unacknowledged assignment count
4. WHEN a Department user views an assignment, THE System SHALL mark the notification as acknowledged
5. THE System SHALL display assignment acknowledgement status on the Head Office Dashboard
6. THE System SHALL display time elapsed since assignment for each unacknowledged assignment
7. WHERE an assignment remains unacknowledged for more than 24 hours, THE System SHALL highlight it with a red indicator

### Requirement 13: Audit Trail Maintenance

**User Story:** As a compliance officer, I want to see a complete audit trail for every task, so that I can demonstrate regulatory compliance and track accountability.

#### Acceptance Criteria

1. THE System SHALL maintain an audit trail for each assignment including all status transitions
2. FOR each audit event, THE System SHALL record: event type, timestamp, responsible user, previous status, new status, remarks
3. THE audit trail SHALL include the following events: Uploaded, AI_Processed, Assigned, Acknowledged, Started, Completed, Verified
4. WHEN a user views assignment details, THE System SHALL display the complete audit trail in chronological order
5. THE System SHALL display the responsible user's full name and username for each audit event
6. THE System SHALL allow filtering audit trails by event type and date range
7. THE System SHALL export audit trails to CSV format when requested

### Requirement 14: PDF Report Generation Parser

**User Story:** As a Head Office user, I want to generate PDF reports for compliance documentation, so that I can provide formal records to regulators and management.

#### Acceptance Criteria

1. THE System SHALL provide a Pretty_Printer for Department Compliance Reports
2. THE System SHALL provide a Pretty_Printer for Executive Compliance Reports
3. THE System SHALL provide a Pretty_Printer for Assignment Summary Reports
4. THE System SHALL provide a Pretty_Printer for MAP Detail Reports
5. FOR ALL valid report data objects, parsing then printing then parsing SHALL produce an equivalent object (round-trip property)
6. THE Department Compliance Report SHALL include: department name, all assigned tasks, status breakdown, completion metrics, timeline
7. THE Executive Compliance Report SHALL include: institution-wide overview, all departments' performance, completion rates, critical items status, trends

### Requirement 15: Report Content Requirements

**User Story:** As a user generating reports, I want comprehensive information included in PDF reports, so that reports serve as complete compliance documentation.

#### Acceptance Criteria

1. ALL reports SHALL include generation timestamp in ISO 8601 format
2. ALL reports SHALL include the generating user's full name and username
3. ALL reports SHALL include completion metrics: total tasks, pending, in progress, completed, verified
4. WHERE a report includes requirements, THE System SHALL display full traceability: circular → requirement → MAP → department
5. WHERE a report includes MAPs, THE System SHALL display MAP title, description, status, priority, responsible parties
6. THE Assignment Summary Report SHALL include: recent assignments, approving user, target departments, current status
7. THE MAP Detail Report SHALL include: MAP details, linked requirements, status history, responsible parties, completion evidence

### Requirement 16: Report Export Fallback

**User Story:** As a developer, I want to cleanly handle incomplete PDF generation functionality, so that users don't encounter broken features.

#### Acceptance Criteria

1. WHERE PDF generation is not fully implemented, THE System SHALL hide the Export button
2. THE System SHALL NOT display non-functional Export buttons on any page
3. WHERE an export feature is unavailable, THE System SHALL log a warning message with the feature name
4. WHEN a user requests an unavailable export, THE System SHALL return HTTP 501 Not Implemented
5. THE System SHALL provide a user-facing message "Export feature coming soon" where export buttons were located
6. WHERE PDF generation fails, THE System SHALL log the error and return a user-friendly error message
7. THE System SHALL allow toggling export buttons via a feature flag in configuration

### Requirement 17: Head Office Role Access Control

**User Story:** As a Head Office user, I want unrestricted access to all system features, so that I can perform all administrative and oversight functions.

#### Acceptance Criteria

1. THE System SHALL allow Head Office users to upload RBI Circulars
2. THE System SHALL allow Head Office users to view AI processing results
3. THE System SHALL allow Head Office users to approve, reassign, or reject assignments
4. THE System SHALL allow Head Office users to verify department completion
5. THE System SHALL allow Head Office users to view the global dashboard
6. THE System SHALL allow Head Office users to view the global knowledge graph
7. THE System SHALL allow Head Office users to view all departments' work

### Requirement 18: Head Office Administrative Capabilities

**User Story:** As a Head Office user, I want to perform administrative operations, so that I can manage the compliance system effectively.

#### Acceptance Criteria

1. THE System SHALL allow Head Office users to generate all types of reports
2. THE System SHALL allow Head Office users to view audit logs for all users
3. THE System SHALL allow Head Office users to manage user accounts
4. THE System SHALL allow Head Office users to view assignment statistics across all departments
5. THE System SHALL allow Head Office users to bulk-approve multiple assignments
6. THE System SHALL allow Head Office users to reassign work between departments
7. THE System SHALL allow Head Office users to modify assignment priorities

### Requirement 19: Department Role Access Control

**User Story:** As a system administrator, I want to enforce strict access controls for Department users, so that information is properly compartmentalized.

#### Acceptance Criteria

1. THE System SHALL allow Department users to view only their assigned work
2. THE System SHALL allow Department users to update task status with the restrictions: Assigned → In_Progress → Completed
3. THE System SHALL allow Department users to search within their assigned items
4. THE System SHALL allow Department users to view their department-scoped knowledge graph
5. THE System SHALL allow Department users to view their Department Dashboard
6. THE System SHALL allow Department users to generate department-specific reports
7. THE System SHALL allow Department users to view their own profile

### Requirement 20: Department Role Access Restrictions

**User Story:** As a security officer, I want to prevent Department users from accessing restricted features, so that data confidentiality is maintained.

#### Acceptance Criteria

1. THE System SHALL prevent Department users from uploading RBI Circulars
2. THE System SHALL prevent Department users from approving assignments
3. THE System SHALL prevent Department users from reassigning work
4. THE System SHALL prevent Department users from verifying completion (marking as Verified)
5. THE System SHALL prevent Department users from viewing other departments' work
6. THE System SHALL prevent Department users from viewing institution-wide analytics
7. THE System SHALL prevent Department users from viewing the global knowledge graph

### Requirement 21: Department Role Administrative Restrictions

**User Story:** As a security officer, I want to prevent Department users from performing administrative operations, so that system integrity is maintained.

#### Acceptance Criteria

1. THE System SHALL prevent Department users from accessing the Head Office Dashboard
2. THE System SHALL prevent Department users from managing user accounts
3. THE System SHALL prevent Department users from viewing other departments' assignments
4. THE System SHALL prevent Department users from modifying assignment priorities
5. THE System SHALL prevent Department users from viewing audit logs for other users
6. WHERE a Department user attempts to access a restricted endpoint, THE System SHALL return HTTP 403 Forbidden with an error message
7. THE System SHALL log all unauthorized access attempts in the audit log

### Requirement 22: Authentication Preservation

**User Story:** As a developer, I want to preserve existing Phase 1 authentication mechanisms, so that security is maintained and no breaking changes occur.

#### Acceptance Criteria

1. THE System SHALL continue to use JWT (JSON Web Tokens) for authentication
2. THE System SHALL continue to use bcrypt for password hashing
3. THE System SHALL continue to use SQLAlchemy ORM for database operations
4. THE System SHALL maintain existing token expiration policies
5. THE System SHALL maintain existing password complexity requirements
6. THE System SHALL maintain existing session management behavior
7. WHEN Phase 2 is deployed, THE System SHALL support all existing Phase 1 user accounts without migration

### Requirement 23: Database Schema Compatibility

**User Story:** As a developer, I want to extend the database schema without breaking changes, so that existing data and functionality remain intact.

#### Acceptance Criteria

1. THE System SHALL only add new tables and columns to the database
2. THE System SHALL NOT remove any existing tables or columns
3. THE System SHALL NOT modify data types of existing columns
4. THE System SHALL NOT modify foreign key relationships of existing tables
5. WHERE new columns are added, THE System SHALL use NULL default values or provide sensible defaults
6. THE System SHALL maintain all existing indexes on tables
7. WHEN Phase 2 is deployed, THE System SHALL execute database migrations automatically without data loss

### Requirement 24: Backend Technology Preservation

**User Story:** As a developer, I want to maintain existing backend technology choices, so that the codebase remains consistent and maintainable.

#### Acceptance Criteria

1. THE System SHALL continue to use FastAPI as the web framework
2. THE System SHALL continue to use SQLAlchemy ORM for database operations
3. THE System SHALL continue to use SQLite as the database engine
4. THE System SHALL maintain existing router structure and naming conventions
5. THE System SHALL maintain existing CRUD operation patterns
6. THE System SHALL continue to use existing middleware for authentication and CORS
7. THE System SHALL maintain compatibility with existing API endpoints

### Requirement 25: Frontend Technology Preservation

**User Story:** As a developer, I want to maintain existing frontend technology choices, so that the UI remains consistent with Phase 1.

#### Acceptance Criteria

1. THE System SHALL continue to use React 18 or higher as the frontend framework
2. THE System SHALL continue to use React Router for navigation
3. THE System SHALL continue to use Axios for API calls
4. THE System SHALL maintain the existing design system and color palette
5. THE System SHALL maintain existing component structure and naming conventions
6. THE System SHALL maintain existing styling approach (inline styles or CSS modules)
7. THE System SHALL ensure new pages follow the same layout patterns as existing pages

### Requirement 26: AI Pipeline Preservation

**User Story:** As a developer, I want to preserve existing AI pipeline scripts, so that regulatory intelligence processing continues to function correctly.

#### Acceptance Criteria

1. THE System SHALL maintain all 42 existing AI pipeline scripts without modification
2. THE System SHALL maintain existing data files totaling approximately 450 MB
3. THE System SHALL maintain existing AI processing workflows for requirement extraction
4. THE System SHALL maintain existing AI processing workflows for MAP generation
5. THE System SHALL maintain existing AI processing workflows for domain classification
6. WHERE new AI functionality is added (department suggestion), THE System SHALL implement it as additional scripts without modifying existing ones
7. THE System SHALL maintain existing data structures for AI processing outputs

### Requirement 27: Real-Time Update Performance

**User Story:** As a user, I want real-time updates to be fast and reliable, so that I have confidence in the displayed information.

#### Acceptance Criteria

1. THE System SHALL use a polling mechanism with a maximum interval of 5 seconds for checking updates
2. WHEN an update is detected, THE System SHALL refresh the affected UI components within 500 milliseconds
3. THE System SHALL batch multiple updates occurring within 2 seconds into a single UI refresh
4. THE System SHALL implement optimistic UI updates that show changes immediately before server confirmation
5. WHERE network latency exceeds 3 seconds, THE System SHALL display a "Syncing..." indicator
6. THE System SHALL handle polling errors gracefully by retrying with exponential backoff up to 30 seconds
7. THE System SHALL stop polling when the browser tab is not visible and resume when the tab becomes active

### Requirement 28: System Performance Requirements

**User Story:** As a user, I want the system to handle realistic workloads efficiently, so that I can work without delays.

#### Acceptance Criteria

1. THE System SHALL support processing 100 or more requirements per circular without performance degradation
2. THE System SHALL support 9 departments simultaneously accessing their dashboards
3. THE System SHALL complete filtering operations on the Assigned Requirements view within 500 milliseconds for datasets up to 500 requirements
4. THE System SHALL complete search operations within 1 second for datasets up to 1000 requirements
5. THE System SHALL render department-scoped knowledge graphs within 3 seconds for graphs with up to 200 nodes
6. THE System SHALL render the global knowledge graph within 5 seconds for graphs with up to 1000 nodes
7. WHEN the database size exceeds 10000 records, THE System SHALL maintain query performance by using appropriate indexes

### Requirement 29: Security Requirements

**User Story:** As a security officer, I want the system to prevent common security vulnerabilities, so that compliance data remains protected.

#### Acceptance Criteria

1. THE System SHALL validate all user inputs to prevent SQL injection attacks
2. THE System SHALL encode all output to prevent cross-site scripting (XSS) attacks
3. THE System SHALL implement CSRF protection for all state-changing operations
4. THE System SHALL enforce HTTPS for all API communication in production environments
5. THE System SHALL log all authentication failures with timestamp, username, and IP address
6. THE System SHALL implement rate limiting of 100 requests per minute per IP address for authentication endpoints
7. THE System SHALL expire JWT tokens after 24 hours of inactivity

### Requirement 30: Deployment Compatibility

**User Story:** As a developer, I want the system to deploy successfully in offline environments, so that it can be used in secure banking networks.

#### Acceptance Criteria

1. THE System SHALL function without requiring internet connectivity
2. THE System SHALL bundle all frontend dependencies in the deployment package
3. THE System SHALL bundle all backend dependencies in the deployment package
4. THE System SHALL NOT require external API calls for core functionality
5. THE System SHALL use local file storage for uploaded documents
6. THE System SHALL use a local SQLite database that requires no external database server
7. WHERE external dependencies are required, THE System SHALL document them in the deployment guide with offline installation instructions
