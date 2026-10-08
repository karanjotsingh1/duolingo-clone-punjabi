# Lingua — English Learning App for Punjabi Speakers

**Lingua** is a full-stack language-learning web application inspired by modern language-learning platforms.

The application helps **Punjabi speakers learn English** through short, interactive lessons, practice exercises, XP, streaks, hearts, achievements, and a leaderboard.

The project is built from scratch with a custom frontend, backend, database, mascot, icons, and learning content.

> **Note:** This project uses original code and original visual assets. No Duolingo source code or Duolingo assets are used.

---

## Live Demo

🔗 **Demo:** `ADD_YOUR_DEPLOYED_FRONTEND_LINK_HERE`

---

## Screenshots

Add your project screenshots here.

```text
screenshots/
├── learning-path.png
├── lesson.png
├── leaderboard.png
└── profile.png
```

You can then add them to this README using:

```md
![Learning Path](screenshots/learning-path.png)
```

---

## Features

### Learning Path

- Course divided into units and skills
- Skills are unlocked step by step
- Locked, available, and completed skill states
- Progress tracking for each skill
- Progress rings and crowns
- Simple and visual learning path

### Interactive Lessons

The application supports five types of exercises:

1. Multiple choice
2. Translation using a word bank
3. Match pairs
4. Fill in the blank
5. Type the answer

Each lesson includes:

- Progress bar
- Instant answer feedback
- Correct and incorrect answer handling
- Keyboard support
- Sound effects
- Text-to-speech for English words
- Repetition of incorrect questions

### Hearts

The learner starts with a limited number of hearts.

- Maximum of 5 hearts
- Wrong answers can reduce hearts
- Hearts regenerate automatically
- Hearts can also be refilled using gems
- Practice mode can give a heart back
- Lessons are blocked when there are no hearts

### XP and Streaks

The application tracks the learner's progress using XP and daily streaks.

- 10 XP for completing a normal lesson
- Extra XP for a perfect lesson
- Daily activity increases the streak
- Missing a day resets the streak
- Longest streak is also tracked

### Daily Goal

Learners can set a daily XP goal.

Available goals include:

- 10 XP
- 20 XP
- 30 XP
- 50 XP

The daily progress is shown in the application.

### Leaderboard

The application includes a weekly leaderboard.

It shows:

- Learner's weekly XP
- Other learners
- Current ranking
- Promotion and demotion zones

### Achievements

The application includes achievement badges.

Achievements are unlocked automatically when the learner reaches specific goals.

Each achievement can include:

- Badge icon
- Progress
- Description
- Gem reward

### Practice Mode

Practice mode allows learners to revise previously learned content.

Practice mode:

- Does not remove hearts
- Provides additional practice
- Can reward a heart

### Timed Mode

Timed practice gives the learner a limited amount of time to answer as many questions as possible.

- 2-minute timer
- Multiple questions
- XP based on performance

### Legendary Mode

Legendary mode is a harder version of a completed skill.

- Available after completing a skill
- Allows only a limited number of mistakes
- Successful completion awards a crown

### Profile and Settings

The profile section displays learner statistics and achievements.

Settings include:

- Display name
- Daily XP goal
- Dark mode
- Sound settings
- Streak testing
- Other placeholder features

### Responsive Design

The application works on desktop and mobile screens.

On smaller screens:

- Sidebar changes to a bottom navigation bar
- Important statistics remain visible at the top
- The lesson interface adjusts to the screen size

---

## Tech Stack

| Part | Technology |
|---|---|
| Frontend | Next.js 14 |
| Language | TypeScript |
| UI | React + CSS |
| Backend | Python |
| API | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | SQLite |
| Testing | Pytest |

---

## Project Structure

```text
lingua/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── learn/
│   │   │   ├── leaderboard/
│   │   │   ├── profile/
│   │   │   ├── settings/
│   │   │   ├── lesson/
│   │   │   └── session/
│   │   │
│   │   ├── components/
│   │   │   ├── LessonPlayer.tsx
│   │   │   ├── SkillNode.tsx
│   │   │   ├── LessonEnd.tsx
│   │   │   ├── Mascot.tsx
│   │   │   ├── exercises.tsx
│   │   │   └── ui.tsx
│   │   │
│   │   └── lib/
│   │       ├── api.ts
│   │       ├── types.ts
│   │       ├── user-context.tsx
│   │       └── sound.ts
│   │
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── services.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── content.py
│   │   └── seed.py
│   │
│   ├── tests/
│   │   └── test_api.py
│   │
│   └── requirements.txt
│
└── README.md
```

---

## How the Application Works

The application has two main parts:

### Frontend

The frontend is responsible for:

- Displaying the learning path
- Showing lessons and exercises
- Managing the lesson interface
- Showing XP, hearts, streaks, and other statistics
- Displaying the leaderboard and profile
- Handling animations, sounds, and user interactions

The frontend communicates with the backend using REST APIs.

### Backend

The backend is responsible for:

- Managing the learner
- Managing course content
- Checking answers
- Managing hearts
- Calculating XP
- Managing streaks
- Unlocking skills
- Managing achievements
- Managing leaderboard data
- Saving learning sessions

This keeps the important game rules on the server.

---

## Database

The project uses **SQLite**.

The database is created automatically when the backend starts.

The main tables are:

```text
courses
   ↓
units
   ↓
skills
   ↓
lessons
   ↓
exercises
   ↓
exercise_options
```

Learner-related data is stored separately:

```text
users
user_skill_progress
study_sessions
achievements
user_achievements
```

The database stores information such as:

- Learner XP
- Hearts
- Gems
- Streak
- Completed lessons
- Skill progress
- Learning sessions
- Achievements

---

## API

The backend provides REST APIs under:

```text
/api
```

Some important endpoints are:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/me` | Get learner information |
| PATCH | `/api/me` | Update learner settings |
| GET | `/api/path` | Get learning path |
| GET | `/api/lessons/{id}` | Get a lesson |
| POST | `/api/exercises/{id}/check` | Check an answer |
| POST | `/api/lessons/{id}/complete` | Complete a lesson |
| GET | `/api/sessions/start` | Start practice/timed/legendary mode |
| POST | `/api/sessions/complete` | Complete a special session |
| POST | `/api/hearts/refill` | Refill hearts |
| GET | `/api/leaderboard` | Get leaderboard |
| GET | `/api/profile` | Get profile and achievements |

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

---

## Important Design Decisions

### Server Controls the Game Rules

The backend is responsible for important game logic.

For example:

- Answer checking
- XP calculation
- Heart changes
- Skill unlocking
- Streak updates
- Achievement unlocking

This prevents the frontend from directly deciding important learner progress.

### Automatic Heart Regeneration

Hearts regenerate based on time.

The application calculates the regeneration when the learner's information is requested, so a separate background job is not required.

### Learning Progress

Learning progress is stored in the database.

The application can determine:

- Which lessons are completed
- Which skills are unlocked
- Daily XP
- Weekly XP
- Current streak
- Achievement progress

---

## Getting Started

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd lingua
```

---

## Backend Setup

Open a terminal and run:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will run at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

## Frontend Setup

Open another terminal:

```bash
cd frontend
```

Create the environment file:

```bash
cp .env.example .env.local
```

Make sure it contains:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The frontend will run at:

```text
http://localhost:3000
```

Open this URL in your browser.

---

## Running Tests

Backend tests can be run using:

```bash
cd backend
pytest -q
```

The tests cover important application flows such as:

- Hearts
- XP
- Streaks
- Skill unlocking
- Legendary mode
- Leaderboard

---

## Seed Data

The database is automatically created and populated when the backend starts for the first time.

The demo learner already has sample progress, so the application can be used immediately.

To reset the database and create the seed data again, delete:

```text
backend/duolingo.db
```

Then restart the backend.

---

## Deployment

### Frontend

The frontend can be deployed using platforms such as **Vercel**.

Set the root directory to:

```text
frontend
```

Add the environment variable:

```env
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL/api
```

### Backend

The backend can be deployed using platforms such as **Render** or **Railway**.

Root directory:

```text
backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The frontend should then use the deployed backend URL in `NEXT_PUBLIC_API_URL`.

> **Note:** The project uses SQLite, so persistent database storage should be considered when deploying to a hosting platform where local files may not persist.

---

## Current Limitations

This is a learning project and some production features are intentionally simplified.

- No real user authentication
- One default learner is used by default
- Gems are a demo currency
- SQLite is used as the database
- Speaking exercises are not implemented yet
- Friends and subscriptions are not implemented
- Some settings are placeholders
- Timed and legendary results are submitted by the frontend
- Text-to-speech uses the browser's built-in functionality

---

## Future Improvements

Possible future improvements include:

- User registration and login
- PostgreSQL database
- Real-time multiplayer leaderboard
- Speaking and pronunciation exercises
- More language courses
- User friends and social features
- Better audio support
- Cloud-based progress synchronization
- More lesson types
- Production-level authentication and security

---

## Project Highlights

This project demonstrates practical experience with:

- Full-stack web development
- Next.js and React
- TypeScript
- REST API development
- FastAPI
- SQLAlchemy
- SQLite database design
- State management
- Game logic
- Progress tracking
- Responsive UI design
- Automated API testing

---

## License

This project was created as a personal/take-home project for learning and demonstration purposes.