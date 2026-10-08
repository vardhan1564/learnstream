# LearnStream Frontend (React 19 + Vite)

## Run locally
```bash
npm install
npm run dev          # http://localhost:5173
```
The app talks to `http://localhost:8080` by default. To change it, copy `.env.example` to `.env` and set `VITE_API_URL`.

## Build for hosting
```bash
npm run build        # output in dist/
```
Upload `dist/` to Netlify, Vercel or any static host. It's a single-page app, so serve `index.html` for all routes
(Netlify: `public/_redirects` is included). Set `VITE_API_URL` to your deployed backend before building, and add the
frontend URL to the backend's `CORS_ORIGINS`.

## Pages
Home, Courses, Course details, Course player, Practice problems + code editor, Quizzes, Roadmaps, Leaderboard,
My learning (dashboard, certificates, account), Certificate verification, and the Admin panel
(overview, courses & videos, MCQ quizzes, coding problems, roadmaps, students, leaderboard).
