# LearnStream Backend (Spring Boot 4, Java 17, MySQL)

## Verified
`mvn clean package` builds with no errors. Every flow was tested end to end against a real running server and database:
sign-up with OTP, login, roles, courses, enrollment, progress, quizzes, certificate PDF and verification, code execution in Java / Python / C++ / JavaScript,
rewards, admin CRUD, password change and reset, rate limiting, and video upload and streaming (local disk and S3 mode).

## Run locally
1. Install Java 17+, MySQL 8 and Maven (or use the included `mvnw`).
2. Copy `secrets.properties.example` to `secrets.properties` in this folder (next to `pom.xml`) and fill in:
   MySQL user/password, Gmail + App Password (for OTP emails), a JWT secret (`openssl rand -hex 32`),
   the first admin email/password, and your Stripe secret key.
   - No Gmail yet? Set `learnstream.mail.enabled=false`: OTP codes are then printed in the server console.
3. Run `./mvnw spring-boot:run` (or run `LearnStreamBackendApplication` from your IDE with this folder as the working directory).
   - The database `learnstream_db` is created automatically.
   - On first start an admin account is created from `learnstream.admin.*`, and sample content
     (4 courses, 8 problems, 2 quizzes, 2 roadmaps) is added so you can test everything. Delete it from the admin panel later.

API runs at http://localhost:8080.

## Rules implemented
| Feature | Rule |
|---|---|
| Accounts | Sign-up always creates a STUDENT. Email OTP (10 min, 5 tries, 60 s resend cooldown). Forgot-password via OTP. Changing the password signs out other devices. |
| Admin | Only `ROLE_ADMIN` can add/edit/delete courses, videos, MCQs, problems, roadmaps; see revenue, students, leaderboard; grant course access; promote admins. |
| Courses | Video links are only sent to enrolled students, admins, or for lessons marked "free preview". |
| Payments | Stripe Checkout. Price comes from the database. Enrollment only after Stripe confirms the session is paid (success page + optional webhook). |
| Rewards | Every 5 distinct solved problems = 1 free-course credit (`learnstream.reward.problems-per-free-course`). |
| MCQs | Correct answers never leave the server. Students only get their score. Attempt limit per quiz. |
| Problems | stdin/stdout tests. Sample tests visible; hidden tests' inputs/outputs are never sent. Java, Python, C++, JavaScript via Judge0. |
| Certificate | All lessons complete + every published course quiz passed. PDF with unique ID; public verification at `/api/certificates/verify/{id}`. |
| Leaderboard | Easy 10 / Medium 20 / Hard 40 points per solved problem + 2 per correct answer (best attempt per quiz). |

## Lesson videos
Each lesson uses either a **video link** (YouTube, Vimeo, Google Drive, direct .mp4) or an **uploaded file**.
Uploaded files are never stored in the database: only a small key like `videos/<id>.mp4` is saved on the lesson.
- `learnstream.storage.type=local` (default): files go to `./uploads/videos` on the server. Fine for development or a VPS with a persistent disk.
- `learnstream.storage.type=s3`: Cloudflare R2 (recommended, no download fees), AWS S3, Backblaze B2... See `secrets.properties.example`.

Students only ever receive a signed link that expires (default 4 hours, `learnstream.storage.url-expiry-minutes`), and only for
lessons they're allowed to watch, so a copied link stops working. Upload limit: 2 GB (`MAX_VIDEO_MB`). Replaced or removed videos are deleted automatically.
Tip: upload MP4 (H.264 + AAC). It plays in every browser and on phones.

## Code execution (Judge0)
Default is the free public instance `https://ce.judge0.com` (rate limited, fine for testing and small classes).
For real traffic use RapidAPI (`judge0.base-url=https://judge0-ce.p.rapidapi.com`, `judge0.api-key`, `judge0.api-host=judge0-ce.p.rapidapi.com`)
or self-host Judge0 with Docker and point `judge0.base-url` at it.

## Deploying
Set environment variables instead of `secrets.properties`: `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `JWT_SECRET`,
`MAIL_USERNAME`, `MAIL_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
`CORS_ORIGINS` (your frontend URL), `FRONTEND_URL`, `BACKEND_URL` (this API's public URL), `SEED_DEMO_DATA=false`,
and for videos `STORAGE_TYPE=s3`, `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`.
If you put Nginx in front, allow big uploads: `client_max_body_size 2g;`.
Behind a proxy, uncomment `server.forward-headers-strategy=native`.
Stripe webhook endpoint: `POST https://<api>/api/payments/webhook`, event `checkout.session.completed`.

Build a jar: `./mvnw clean package`, then run `java -jar target/LearnStream-Backend-0.0.1-SNAPSHOT.jar`
from a folder containing `secrets.properties` (or with the environment variables set).
