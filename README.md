# Little-Lemon-Django-App
The Little Lemon restaurant website. Book a table (reservation). A back-end app

## Installation and Setup

Follow these steps to get a development environment running:

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install django
    pip install mysql
    pip install djangorestframework
    pip install djoser
    ```

3.  **Apply migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
    *(Follow the prompts to create username, email, and password.)*

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

6.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:8000/` (or the specific app URL like `/restaurant/`).
    Access the Django Admin at `http://127.0.0.1:8000/admin/`.
    Other API paths that peers can check:
    ```bash
    `/restaurant/`
    `/restaurant/api/menu/`
    `/restaurant/api/menu/id` replace id with the corresponding number
    `/restaurant/api/booking/tables/`
    `/auth/users/`
    `/api-token-auth/` not meant for retrieving (GET). make POST calls with this in Insomnia instead to get token
    `/auth/token/login/` token create
    ```
