# Launch Fair Billing — Online Version

This folder contains the Streamlit web version of the Launch Fair Billing software. `FAIR.PY` is the original desktop app; `app.py` is the online app.

## 1. Create the online database

1. Create a free project at [Supabase](https://supabase.com/).
2. In the project, open **SQL Editor** → **New query**.
3. Open `supabase_schema.sql`, copy all its contents, paste them into Supabase, and click **Run**.
4. Open **Project Settings** → **API** and copy the **Project URL** and **anon public key**.

Never use the `service_role` key in this app or share it with anyone.

## 2. Test on your computer (optional)

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
2. Put the real Supabase URL/key in `secrets.toml`.
3. In this folder, run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 3. Put it on GitHub

1. Create a **private** GitHub repository named `launch-fair-billing`.
2. Upload all files in this folder except `.streamlit/secrets.toml` and the original Excel data files.
3. Confirm GitHub has: `app.py`, `requirements.txt`, `supabase_schema.sql`, `.streamlit/config.toml`, and `.gitignore`.

## 4. Deploy to Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) using the same GitHub account.
2. Click **Create app**, select the repository, branch, and `app.py`.
3. Before deploying, open **Advanced settings** → **Secrets**, then paste:

```toml
SUPABASE_URL = "your-real-project-url"
SUPABASE_KEY = "your-real-anon-public-key"
APP_PASSWORD = "your-customer-test-password"
```

4. Click **Deploy**. Share the generated `streamlit.app` link with the customer.

## Important security note

The SQL policies in `supabase_schema.sql` are intentionally simple for a short customer test. Before using this for real business data or multiple customers, add proper user accounts and strict Supabase Row Level Security policies.
