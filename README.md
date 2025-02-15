# SaaS Launchpad

A modern, production-ready boilerplate to kickstart your SaaS application development. Built with Next.js, FastAPI, and PostgreSQL.

## Features

### Authentication & Authorization

- Complete OAuth2 authentication system
- Multiple sign-in options:
  - Email/password authentication
  - Google Sign-In integration
- Secure JWT-based session management
- Protected API routes and middleware
- Automatic token refresh

### Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL
- **Styling**: Tailwind CSS with shadcn/ui components
  - Pre-configured shadcn/ui theme
  - Ready-to-use components like buttons, forms, dialogs
  - Consistent design system
  - Dark mode support

### Developer Experience

- Type-safe API calls
- Environment configuration
- Modern UI components
- Responsive design out of the box
- Docker development environment

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/saas-launchpad.git
   cd saas-launchpad
   ```

2. Set up the backend:

   ```bash
   cd backend
   docker compose up -d
   ```

3. Set up the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open your browser and navigate to:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
