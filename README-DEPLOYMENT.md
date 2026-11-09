# Portfolio deployment notes

The redesigned portfolio is being developed on the `redesign/homepage-v1` branch. The live `main` branch is not changed by this work.

## Frontend (GitHub Pages)

1. Keep the static site published from the repository's `main` branch until the redesign is reviewed.
2. When ready, merge the approved redesign branch and confirm GitHub Pages is configured to publish the repository root.
3. The canonical site URL is `https://ajayvarmanm.github.io/Portfolio/`.

## Django contact API (Render or another Python host)

The Django API is separate from GitHub Pages. Before deploying:

1. Create a PostgreSQL database and copy its internal connection URL into `DATABASE_URL`.
2. Create a Python web service from this repository's approved branch.
3. Build command: `pip install -r requirements.txt && python manage.py migrate`
4. Start command: `gunicorn portfolio_backend.wsgi:application`
5. Configure environment variables:
   - `DJANGO_SECRET_KEY`: a newly generated, private Django secret.
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: the backend hostname, e.g. `your-service.onrender.com`
   - `FRONTEND_ORIGINS`: `https://ajayvarmanm.github.io`
   - `DATABASE_URL`: the PostgreSQL connection URL.
6. After deployment, set `CONTACT_API_BASE_URL` in `assets/js/main.js` to the backend origin (for example, `https://your-service.onrender.com`), then commit the change.

Do not commit production secrets or database URLs. SQLite is retained only as a local-development fallback; use persistent PostgreSQL for production so contact submissions are not lost when a host restarts.

## Contact form

The form validates input on the server, checks the browser origin against `FRONTEND_ORIGINS`, limits request size and message lengths, and includes a honeypot field. It stores submissions in the `Contact` model, viewable through Django admin after an admin user is created.

The form deliberately stays disconnected until a real backend URL and production environment are configured. Visitors can use the direct email link in the meantime.

## SEO files

- `robots.txt` points crawlers to the XML sitemap.
- `sitemap.xml` currently lists the single-page portfolio URL.
- Canonical, Open Graph, Twitter card and Person structured data are in `index.html`.
