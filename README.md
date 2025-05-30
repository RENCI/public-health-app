# ACCIDDA

## 🚧 Development

1. clone this repo & move into project dir
2. start virtual environment, `pipenv shell` ([Pipenv](https://pipenv.pypa.io/en/latest/) or other virtualenv management tool)
3. install deps, `pipenv install`
4. start dev server, `python app.py`

```bash
$ python app.py
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: on
```

5. `Ctrl/⌘ + D` exits the virtual environment

## 📦 Production

A Makefile exists to make building for production and deployment simpler.
Use `make help` to see a list of available targets.

```bash
$ make help

Help Commands
• help                 📖 Show help

General Commands
• requirements         🔐 Generate requirements.txt from Pipfile.lock (with Pipenv)

Docker Commands
• build                🛠️  Build Docker image
• run                  ▶️  Run Docker container
• stop                 🛑 Stop the running container
• push                 📤 Push the Docker image
• publish              📤 Build and push the Docker image

Helm Commands
• pod-up               🚀 Install or upgrade Helm release
• pod-down             💣 Uninstall Helm release
```

A few notes about building Docker images: The image build uses pip (not Pipenv), which relies on a `requirements.txt` file, so the first step to build an image is to create that. Our Make target `make requirements` leverages Pipenv to create that file. If you are not using Pipenv, use the analogoous command for your local setup.
