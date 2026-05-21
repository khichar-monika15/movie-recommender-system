# Deployment Guide — All 3 Projects

Follow this guide in order. Each section has exact steps with nothing skipped.
Copy any step to ChatGPT if you get stuck — just paste the heading + step number.

---

## Part 0 — Accounts to Create Before Starting

You need these 4 free accounts. Create all of them first.

| Account | Link | Used For |
|---|---|---|
| MongoDB Atlas | https://cloud.mongodb.com | Social Media + UMS databases |
| Cloudinary | https://cloudinary.com | Social Media photo storage |
| Render | https://render.com | Node.js backends |
| Vercel | https://vercel.com | UMS React frontend |

Streamlit Community Cloud (https://share.streamlit.io) — sign in with your GitHub account (khichar-monika15).

---

## Part 1 — MongoDB Atlas Setup (one cluster for both projects)

1. Go to https://cloud.mongodb.com → Sign up or log in.
2. Click **Create** → choose **M0 Free** tier → pick any region → click **Create Deployment**.
3. It asks you to create a database user:
   - Username: `monika` (or anything)
   - Password: click **Autogenerate Secure Password** → **copy and save this password somewhere**
   - Click **Create Database User**
4. Then it asks where you'll connect from. Choose **My Local Environment**, add IP `0.0.0.0/0` (means anywhere), click **Add Entry** → **Finish and Close**.
5. Click **Connect** on your cluster → **Drivers** → copy the connection string. It looks like:
   ```
   mongodb+srv://monika:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with the actual password you saved in step 3.
7. Add a database name before the `?` — use `social` for social media and `ums` for UMS:
   - Social media URI: `mongodb+srv://monika:YOURPASS@cluster0.xxx.mongodb.net/social?retryWrites=true&w=majority`
   - UMS URI: `mongodb+srv://monika:YOURPASS@cluster0.xxx.mongodb.net/ums?retryWrites=true&w=majority`

Save both URIs. You will paste them into the `.env` files in the next parts.

---

## Part 2 — Cloudinary Setup (for Social Media only)

1. Go to https://cloudinary.com → Sign up or log in.
2. After login, you land on the **Dashboard**. You will see:
   - **Cloud Name** — a short word like `dxyz12345`
   - **API Key** — a long number
   - **API Secret** — click "Reveal" to see it
3. Copy all three. You will paste them in Part 4.

---

## Part 3 — Movie Recommender (deploy this first — easiest)

### Step 3a — Generate the model files (do this on Kaggle)

The model `.pkl` files are not in the repo because they are too large. You need to generate them from the Kaggle notebook.

1. Go to https://www.kaggle.com and log in.
2. Open your movie recommender notebook (the one you built earlier).
3. Scroll to the very end. Find where it has these two lines:
   ```python
   pickle.dump(new_df, open('movie_list.pkl', 'wb'))
   pickle.dump(similarity, open('similarity.pkl', 'wb'))
   ```
4. Add these 2 lines **right after** those two lines:
   ```python
   pickle.dump(cv, open('vectorizer.pkl', 'wb'))
   pickle.dump(vectors.toarray(), open('vectors.pkl', 'wb'))
   ```
   Note: `cv` is your CountVectorizer variable. `vectors` is the result of `cv.fit_transform(...)`. Check your notebook for the exact variable names if they're different.
5. Run all cells (Runtime → Run all / Restart and run all).
6. After it finishes, download all 4 pkl files:
   - `movie_list.pkl`
   - `similarity.pkl`
   - `vectorizer.pkl`
   - `vectors.pkl`

### Step 3b — Add pkl files to the GitHub repo

The repo already has Git LFS set up for the large files. Follow these steps exactly.

Open a terminal and run:

```bash
cd /tmp
git clone https://github.com/khichar-monika15/movie-recommender-system.git movie-rec
cd movie-rec
```

Copy your 4 downloaded pkl files into the `model/` folder inside this directory. Then:

```bash
git add model/movie_list.pkl model/similarity.pkl model/vectorizer.pkl model/vectors.pkl
git commit -m "Add model pkl files"
git -c credential.helper="" push "https://khichar-monika15:YOUR_TOKEN@github.com/khichar-monika15/movie-recommender-system.git" main
```

Replace `YOUR_TOKEN` with your GitHub classic PAT (the one with `repo` scope).

The push will take a few minutes because of LFS (large files). Wait for it to finish.

### Step 3c — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io → sign in with GitHub (khichar-monika15).
2. Click **New app**.
3. Fill in:
   - **Repository**: `khichar-monika15/movie-recommender-system`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Deploy**.
5. Wait ~2 minutes. It installs requirements and launches.
6. You get a public URL like `https://khichar-monika15-movie-recommender-system-app-xxxx.streamlit.app`.

**Test it**: Type "Dhurandhar 2" in the search box → click Show Recommendations → it should show a spinner then 5 results.

Movie recommender is done.

---

## Part 4 — Social Media App (Render — single service)

### Step 4a — Fill in the .env file

Open the file `mern-social-media-main/backend/.env` and fill in the real values:

```
PORT=7000
MONGO_URL=mongodb+srv://monika:YOURPASS@cluster0.xxx.mongodb.net/social?retryWrites=true&w=majority
JWT_SEC=anyrandom32characterstringlikethisone1234
Cloudinary_Cloud_Name=your_cloud_name_from_cloudinary_dashboard
Cloudinary_Api=your_api_key_from_cloudinary_dashboard
Cloudinary_Secret=your_api_secret_from_cloudinary_dashboard
SELF_URL=http://localhost:7000
```

This file is in `.gitignore` — it will NOT be pushed to GitHub. It's only for local testing.

### Step 4b — Deploy on Render

1. Go to https://render.com → log in (create account if needed).
2. Click **New** → **Web Service**.
3. Connect your GitHub account when asked → find the repo `khichar-monika15/mern-social-media`.
4. Fill in these fields:
   - **Name**: `mern-social-media` (or anything)
   - **Root Directory**: `mern-social-media-main`
   - **Runtime**: `Node`
   - **Build Command**:
     ```
     npm install && cd frontend && npm install && npm run build && cd ..
     ```
   - **Start Command**:
     ```
     node backend/index.js
     ```
5. Scroll down to **Environment Variables**. Add these one by one (click **Add Environment Variable** for each):

   | Key | Value |
   |---|---|
   | `MONGO_URL` | your MongoDB Atlas URI (with `/social?`) |
   | `JWT_SEC` | any random 32+ character string |
   | `Cloudinary_Cloud_Name` | from Cloudinary dashboard |
   | `Cloudinary_Api` | from Cloudinary dashboard |
   | `Cloudinary_Secret` | from Cloudinary dashboard |
   | `SELF_URL` | leave blank for now — fill after deploy |

6. Click **Create Web Service**.
7. Wait 5-10 minutes for the first build. Watch the logs — it should say `Server is running on port 10000` at the end.
8. Copy the URL Render gives you — it looks like `https://mern-social-media-xxxx.onrender.com`.

### Step 4c — Update SELF_URL

1. In Render → your service → **Environment** tab.
2. Find `SELF_URL` → click Edit → paste the full Render URL: `https://mern-social-media-xxxx.onrender.com`
3. Click **Save Changes** → Render will redeploy automatically (1-2 min).

**Test it**: Open the Render URL in browser → you should see the social media app login page.

Social media app is done.

---

## Part 5 — University Management System

This project has two deploys: backend on Render, frontend on Vercel.

### Step 5a — Fill in the .env files

**Backend** — open `university-management-system-main/server/.env`:
```
PORT=4000
DATABASE_CONNECTION_STRING=mongodb+srv://monika:YOURPASS@cluster0.xxx.mongodb.net/ums?retryWrites=true&w=majority
```

**Frontend** — open `university-management-system-main/client/.env`:
```
REACT_APP_API_URL=http://localhost:4000/v1/api/
```
(This is for local testing only. You will update the URL in Vercel after deploy.)

### Step 5b — Deploy backend on Render

1. Render → **New** → **Web Service**.
2. Connect GitHub → find `khichar-monika15/university-management-system`.
3. Fill in:
   - **Root Directory**: `university-management-system-main/server`
   - **Runtime**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `node index.js`
4. Add environment variables:

   | Key | Value |
   |---|---|
   | `DATABASE_CONNECTION_STRING` | your MongoDB Atlas URI (with `/ums?`) |

5. Click **Create Web Service**.
6. Wait for deploy. Copy the URL — looks like `https://university-management-system-xxxx.onrender.com`.

### Step 5c — Deploy frontend on Vercel

1. Go to https://vercel.com → log in → **Add New** → **Project**.
2. Click **Import Git Repository** → connect GitHub → find `khichar-monika15/university-management-system`.
3. Fill in:
   - **Root Directory**: click **Edit** → type `university-management-system-main/client` → click **Continue**
   - **Framework Preset**: Create React App (Vercel should detect this automatically)
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. Before clicking Deploy, scroll to **Environment Variables**:
   - Key: `REACT_APP_API_URL`
   - Value: `https://university-management-system-xxxx.onrender.com/v1/api/`
   (Use the actual Render URL you copied in Step 5b — put `/v1/api/` at the end)
5. Click **Deploy**.
6. Wait ~2 minutes. Vercel gives you a URL like `https://university-management-system-xxxx.vercel.app`.

**Test it**: Open the Vercel URL → you should see the UMS home page with login options for Admin, Instructor, Student.

UMS is done.

---

## Part 6 — Create Test Accounts for Demo

### Social Media
1. Open your Render URL.
2. Register Account 1 (for demo — the main account).
3. Open an incognito window → Register Account 2 (to demo real-time likes/notifications).

### University Management
1. Open your Vercel URL.
2. Go to Admin Login → you need to create an admin account first.
   - The first admin account is created via the `/admin/register` route directly.
   - Open: `https://university-management-system-xxxx.vercel.app/admin/register`
   - Fill in the form → register.
3. Log in as Admin → create 1 instructor + 2-3 courses.
4. Go to Instructor Login → log in as the instructor you created.
5. Go to Student Login → register a new student account → register for a course.

---

## Quick Reference — All Live URLs

Fill this in after deploying:

| App | Live URL |
|---|---|
| Social Media | `https://_____________________.onrender.com` |
| UMS Frontend | `https://_____________________.vercel.app` |
| Movie Recommender | `https://_____________________.streamlit.app` |

---

## If Something Breaks

- **Render deploy failed**: Click **Logs** on the service page. Copy the error and paste to ChatGPT with the message: "My Render deployment failed. Here is the error: [paste log]"
- **MongoDB connection error**: Check that your Atlas IP whitelist has `0.0.0.0/0` (allow from anywhere). Also check the URI has the correct password and database name.
- **Vercel build failed**: Check the build logs in Vercel dashboard. Most common cause is wrong Root Directory.
- **Streamlit app crashes**: Check that all 4 pkl files are present in the `model/` folder on GitHub.
- **Social media not loading**: Check Render logs for the backend. Most likely MongoDB URI is wrong or Cloudinary keys are missing.
