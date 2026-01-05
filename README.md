# ACCIDDA

## 🚧 Development

1. clone this repo & move into project dir
2. install uv [here](https://docs.astral.sh/uv/getting-started/installation/) (I recommend the standalone install script)
3. create virtual environment and install deps, `uv sync`
4. start dev server, `uv run python app.py`

You might need to manually reselect the python interpreter in your IDE. The python executable will be at `./.venv/bin/python` by default.

```bash
$ uv run python app.py
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: on
```

5. `Ctrl/⌘ + D` exits the virtual environment
6. If using VSCode you can install the Ruff extension [here](https://marketplace.cursorapi.com/items/?itemName=charliermarsh.ruff). You can then set the following settings in VSCode to use it: 
```json
"[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
    "editor.codeActionsOnSave": { 
        "source.organizeImports": "explicit"
    }
},
```

If not using VSCode, you can use the ruff linter and formatter with the following commands
```bash
ruff check      # linting
ruff format .   # formatting
```
As a convenience, you can use the make target `make ruff` to do both simultaneously.

## 🧾 PDF Generation

We use [Weasyprint](https://doc.courtbouillon.org/weasyprint/stable/index.html) for generating PDFs.

WeasyPrint depends on a few system libraries for handling layout, fonts, and CSS rendering.
They are installed into the production build, and must be installed locally for PDF generation
to function in your local development environment. See the [Weasyprint installation instructions](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for bootstrapping your system

## 📦 Production

A Makefile exists to make building for production and deployment simpler.
Use `make help` to see a list of available targets.

```
$ make help

Help Commands
• help                  📖 Show help

General Commands
• lint                  🤔 Run linter
• format                ℹ︎ Run formatter
• ruff                  🔀 Run linter and formatter
• test                  🧪 Run tests

Docker Commands
• build                 🛠️ Build Docker image
• run                   ▶️ Run Docker container
• stop                  🛑 Stop the running container
• push                  📤 Push the Docker image
• publish               📤 Build and push the Docker image

Helm Commands
• pod-up                🚀 Install or upgrade Helm release
• pod-down              💣 Uninstall Helm release
```
