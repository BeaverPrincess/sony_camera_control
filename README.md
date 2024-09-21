## Setup Instructions

1. **Clone the repository:**

    ```bash
    git clone https://github.com/BeaverPrincess/sony_camera_control.git
    cd sony_camera_control
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

    ```windows
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Migrate the models:**

    ```bash
    python manage.py migrate
    ```

5. **Run the project:**

    ```bash
    python manage.py runserver
    ```