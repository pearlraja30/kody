# Running Kodys Project with Docker (Legacy Python 2.7)

This project is a legacy Django 1.11 application running on Python 2.7. To ensure compatibility across different operating systems (especially modern macOS), we use Docker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## How to Run

1.  **Open Terminal** in the project root directory.
2.  **Build and Start** the container:
    ```bash
    docker-compose up --build
    ```
3.  **Access the Application**:
    Once the logs show the server is running, open your browser and go to:
    [http://localhost:5423](http://localhost:5423)

## Project Structure (for Docker)

- `Dockerfile`: Defines the Python 2.7 environment and installs dependencies.
- `docker-compose.yml`: Configures volume mapping and port forwarding.
- `app/appsource/db.sqlite3`: The local database file.

## Troubleshooting

- **Port Conflict**: If port 5423 is already in use, you can change it in `docker-compose.yml` under the `ports` section.
- **Logs**: Use `docker-compose logs -f` to see real-time output from the Django server.
