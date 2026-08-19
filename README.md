# LedgerFlowPro — Online Version (Multi-User)

This folder contains the Streamlit web version of the billing software.
`FAIR.PY` is the original desktop app; `app.py` is the online app.

Every visitor now creates their **own account** (email + password) on first
visit and only ever sees **their own** parties, bills, and payments. There is
no shared password anymore.

## 1. Create / update the online database

1. Go to your Supabase project → **SQL Editor** → **New query**.
2. Open `supabase_schema.sql`, copy all its contents, paste them in, and
   click **Run**. This works whether it's a brand-new project or one where
   you already ran the old single-password version of this file — it only
   adds what's missing (the `user_id` ownership column and new security
   rules).
3. If this is an existing project with real bills already in it, see the
   optional "claim your old rows" note at the bottom of `supabase_schema.sql`.

## 2. Turn off email confirmation (recommended for a quick launch)

By default Supabase makes new users click a confirmation link in their email
before they can log in. For a simple business app this is usually extra
friction you don't need:

1. Supabase dashboard → **Authentication** → **Providers** → **Email**.
2. Turn **off** "Confirm email".
3. Save.

With this off, signup logs the person straight in. If you leave it on,
new users will see "check your email" after signing up, and must click the
link before their first login.

## 3. Test on your computer (optional)

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
2. Put the real Supabase URL/key in `secrets.toml`.
3. In this folder, run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 4. Put it on GitHub

1. Create a **private** GitHub repository.
2. Upload all files in this folder except `.streamlit/secrets.toml` and any
   original Excel data files.
3. Confirm GitHub has: `app.py`, `requirements.txt`, `supabase_schema.sql`,
   `.streamlit/config.toml`, and `.gitignore`.

## 5. Deploy to Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) using the
   same GitHub account.
2. Click **Create app**, select the repository, branch, and `app.py`.
3. Before deploying, open **Advanced settings** → **Secrets**, then paste:

```toml
SUPABASE_URL = "your-real-project-url"
SUPABASE_KEY = "your-real-anon-public-key"
```

(The old `APP_PASSWORD` secret is no longer used — you can delete it.)

4. Click **Deploy**. Share the generated `streamlit.app` link. Anyone who
   opens it will see **Login** / **Naya Account Banayein** (Sign Up) tabs and
   must create their own account before using the app.

## How the data isolation works

- Each table (`parties`, `bills`, `payments`) has a `user_id` column that is
  filled in automatically with whoever is logged in.
- Row Level Security (RLS) policies in Supabase enforce, at the database
  level, that a logged-in user can only ever `select`/`insert`/`update`/
  `delete` rows where `user_id` matches their own account. This is enforced
  by the database itself, not just the app's screens — so it holds even if
  someone tries to call the API directly.

## Notes / limits of this version

- If a user hard-refreshes the browser tab, they'll be asked to log in again
  (sessions aren't persisted across a full page reload yet).
- There's no "forgot password" screen yet — that can be added later using
  Supabase's password-reset email flow if you need it.
