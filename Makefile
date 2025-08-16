# ============
# 📦 AUTOPHONY
# Auto-detect targets with help comments
PHONY_TARGETS := $(shell awk -F':.*?##' '/^[a-zA-Z0-9_.-]+:.*##/ {print $$1}' $(MAKEFILE_LIST))
.PHONY: help $(PHONY_TARGETS)
# ============

# ============
# ⚙️ CONFIG
APP_NAME := accidda-ui
TAG := 0.6.0
IMAGE_NAME := containers.renci.org/comms/$(APP_NAME):$(TAG)
PORT := 80
RELEASE_NAME ?= $(APP_NAME)
# ============

##@ Help Commands

help: ## 📖 Show help
	@awk ' \
		BEGIN {FS = ":.*?## "}; \
		/^[a-zA-Z0-9_.-]+:.*?##/ {printf "• \033[36m%-20s\033[0m %s\n", $$1, $$2}; \
		/^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)} \
	' $(MAKEFILE_LIST)

##@ General Commands

requirements: ## 🔐 Generate requirements.txt from Pipfile.lock (with Pipenv)
	@command -v pipenv >/dev/null 2>&1 || { echo >&2 "pipenv not installed."; exit 1; }
	pipenv requirements > requirements.txt

##@ Docker Commands

build: requirements ## 🛠️  Build Docker image
	docker build -t $(IMAGE_NAME) .

run: ## ▶️  Run Docker container
	docker run --rm --name $(APP_NAME) -it -p $(PORT):8050 $(IMAGE_NAME)

stop: ## 🛑 Stop the running container
	@echo "🛑 Stopping Docker container '$(APP_NAME)' if running"
	docker ps -q -f name=$(APP_NAME) | grep -q . && docker stop $(APP_NAME)

push: ## 📤 Push the Docker image
	@echo "📦 Pushing Docker image $(IMAGE_NAME)"
	docker push $(IMAGE_NAME)

publish: build push ## 📤 Build and push the Docker image

##@ Helm Commands

pod-up: ## 🚀 Install or upgrade Helm release
	@echo "📦 Using Helm values file: $(VALUES_FILE)"
	@if [ -f $(VALUES_FILE) ]; then \
		echo "🔄 Installing or upgrading Helm release '$(RELEASE_NAME)'"; \
		helm upgrade --install $(RELEASE_NAME) k8s/chart -n comms; \
	else \
		echo "❌ Error: Values file not found: $(VALUES_FILE)"; \
		exit 1; \
	fi

pod-down: ## 💣 Uninstall Helm release
	@echo "🗑️  Uninstalling Helm release '$(RELEASE_NAME)'"
	-helm uninstall $(RELEASE_NAME) -n comms || true
