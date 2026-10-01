# MSMT Nepal website

A fresh Django and Wagtail rebuild of the MSMT Nepal public website. It uses PostgreSQL in production, Wagtail for editorial management, Django templates and CSS for the public pages, and Passenger WSGI for cPanel hosting.

## Pages and editing

The Wagtail admin is at `/admin/`. The public page tree has the homepage and the sections `/about/`, `/our-team/`, `/services/`, `/notices/`, `/media/`, and `/contact/`. Django's slash handling also redirects the live site's slashless section URLs to these paths. Service, team member, notice, and media detail pages are created underneath their section and get normal Wagtail draft, preview, revision, and publishing controls.

Editors can update:

- Homepage headline, introduction, image, purpose, service and approach text.
- About and section introductions and rich text.
- Service entries and their current/confirm status.
- Team member roles, biographies, portraits and order.
- Notices, dates, rich text and downloadable documents.
- Media stories, photographs, documents and external resource links.
- Site-wide office contact details, map link, social links, footer text and footer note.

Contact inquiries are stored in PostgreSQL and are visible to administrators in `/django-admin/`. The form asks visitors not to submit health records and is not for urgent care. No email delivery service is configured.

## Local setup

Requirements: Python 3.10–3.14, pip, and PostgreSQL for a production-like local database. The application has a SQLite fallback for a quick local preview when `DATABASE_URL` is unset.

1. Create and activate a virtual environment, then install `requirements.txt`.
2. Copy `.env.example` to `.env`. Set a random `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=true`, `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`, and your local `DATABASE_URL` if using PostgreSQL. Local SQLite is used if you leave the database URL blank.
3. Run the initial database migrations:

   ```sh
   python manage.py migrate
   ```

4. Create the first Wagtail administrator. There is no default login:

   ```sh
   python manage.py createsuperuser
   ```

5. Create the editable starter pages and fresh introductory content:

   ```sh
   python manage.py seed_site
   ```

   The command is safe to rerun: it does not overwrite content or create duplicate starter records. It creates the page tree and service descriptions from the live public site. It does not import a database, team records, old repository content, notices, or media stories.

6. Run the local server with `python manage.py runserver`, then open `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/admin/`.

## Editors and administrator access

Create a Wagtail group in **Settings → Groups**, for example **Website Editors**. Assign page **Add** and **Edit** rights at the MSMT Nepal homepage so they cascade to the child sections. Assign **Publish** only to trusted editors who should publish directly; without that permission, their changes remain drafts for an administrator to review and publish. Grant add/edit access to the Images and Documents collections for editors who upload approved assets. Do not grant user/group administration or Django admin access to this group. Superusers retain user, site, group, and system administration.

Wagtail pages and their detail records use Wagtail's page revision and publishing workflow. Editors should create or edit a page, preview it, then publish it if their role has publishing permission. New content remains out of the public site until published.

## cPanel / Passenger deployment

Confirm with the hosting provider that the account has a Python App/Passenger runtime for Python 3.10–3.14 and PostgreSQL access. Use a supported Python 3.11 or 3.12 if that is the provider's latest available option.

1. Create a PostgreSQL database and application user in cPanel. Start with a clean schema for this fresh build. Do not point the application at an existing production site's database.
2. In **Setup Python App**, select the Python version, set the application root to this project, select the public domain/path, and use `passenger_wsgi.py` as the startup file with `application` as the WSGI callable.
3. Install the dependencies from cPanel Terminal using the app's virtualenv interpreter:

   ```sh
   pip install -r requirements.txt
   ```

4. Set the application environment variables in cPanel. `.env.example` contains variable names only. Set:

   - `DJANGO_SECRET_KEY`: a long, random, unique value.
   - `DJANGO_DEBUG`: `false`.
   - `DJANGO_ALLOWED_HOSTS`: the bare domain names, comma-separated (for example `example.org,www.example.org`).
   - `CSRF_TRUSTED_ORIGINS`: full HTTPS origins, comma-separated (for example `https://example.org,https://www.example.org`).
   - `DATABASE_URL`: `postgresql://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME`; URL-encode special characters in the username or password.
   - `DB_SSL`: `true` if required by the database host; otherwise `false`.
   - `MEDIA_ROOT`: an absolute, writable path outside the code checkout and deployment directory, such as `/home/CPANELUSER/msmt-media`.
   - `WAGTAILADMIN_BASE_URL`: the public HTTPS site URL.

   Do not put secrets in the repository or deploy hook. Keep `MEDIA_ROOT` persistent through releases, ensure the Passenger account can write to it, and include it in the hosting backup policy. Public uploads are served from this persistent directory; the app can also be configured to serve the same URL path directly through Apache if the host provides a persistent media alias.

5. Apply Django and Wagtail migrations to the clean PostgreSQL database:

   ```sh
   python manage.py migrate
   ```

6. Create the first administrator and seed the editable page tree:

   ```sh
   python manage.py createsuperuser
   python manage.py seed_site
   ```

   Sign in at `https://YOUR-DOMAIN/admin/`, configure a Website Editors group, and review/publish page content. The contact details and starter service descriptions are editable.

7. Build the static asset manifest and restart Passenger after code changes:

   ```sh
   python manage.py collectstatic --noinput
   mkdir -p tmp && touch tmp/restart.txt
   ```

   cPanel may create the Passenger restart file automatically. Use the host's documented restart method if it differs. Keep uploaded files out of the release/build directory; deploy code without replacing the media directory.

For future model changes, create and commit a Django migration with `python manage.py makemigrations`, then apply it with `python manage.py migrate` during the release. Back up the database before production schema changes.

## Branding and content still needed

The official MSMT emblem was available on the live site and is included in `static/images/msmt-logo.png`. The live homepage photograph has not been bundled because the supplied repository's asset notes say there were no approved MSMT photographs. A CSS clinic illustration fills the hero until an approved clinic/community photo is supplied. No staff names, bios, portraits, partner marks, testimonials, certifications, or media stories are fabricated or preloaded. The team, notices, and media sections show clear empty states until approved content is added. Confirm all contact details and service availability before launch.

## Runtime notes

- `passenger_wsgi.py` is the cPanel Passenger entry point.
- PostgreSQL is configured through `DATABASE_URL`; SQLite is only a local convenience fallback.
- Wagtail uploads use `MEDIA_ROOT`, which must be persistent and writable on cPanel.
- Static CSS, JavaScript, and the logo are collected to `staticfiles/` and served using WhiteNoise.
- The contact form stores inquiries in PostgreSQL for an administrator. SMTP notifications are not configured.
- No production deployment, database import, remote commit, or push was performed.
