# ============
# 📦 AUTOPHONY
# Auto-detect targets with help comments
# PHONY_TARGETS := $(shell awk -F':.*?##' '/^[a-zA-Z0-9_.-]+:.*##/ {print $$1}' $(MAKEFILE_LIST))
.PHONY: help $(PHONY_TARGETS)
# ============

# ============
# ⚙️ CONFIG
APP_NAME := accidda-ui
TAG := 0.6.0-dev
IMAGE_NAME := containers.renci.org/comms/$(APP_NAME):$(TAG)
PORT := 80
RELEASE_NAME ?= $(APP_NAME)
NAMESPACE ?= comms
# ============

##@ Help Commands

help: ## 📖 Show help
	@awk ' \
		BEGIN {FS = ":.*?## "}; \
		/^[a-zA-Z0-9_.-]+:.*?##/ {printf "• \033[36m%-20s\033[0m %s\n", $$1, $$2}; \
		/^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)} \
	' $(MAKEFILE_LIST)

##@ General Commands

lint: ## 🤔 Run linter
	@uv run ruff check .

format: ## ℹ︎ Run formatter
	@uv run ruff format .

ruff: lint format ## 🔀 Run linter and formatter

dev: ## 🏃‍♂️ Run locally using uv
	@uv run python app.py

test: ## 🧪 Run tests
	@uv run pytest .

##@ Docker Commands

build: ## 🛠️  Build Docker image
	docker build \
		-t $(IMAGE_NAME) \
		--platform linux/amd64 \
		.

run: ## ▶️  Run Docker container
	docker run \
		--rm \
		--platform linux/amd64 \
		--name $(APP_NAME) \
		-it \
		-p $(PORT):8050 \
		$(IMAGE_NAME)

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
		helm upgrade --install $(RELEASE_NAME) k8s/chart -n $(NAMESPACE); \
	else \
		echo "❌ Error: Values file not found: $(VALUES_FILE)"; \
		exit 1; \
	fi

pod-down: ## 💣 Uninstall Helm release
	@echo "🗑️  Uninstalling Helm release '$(RELEASE_NAME)'"
	-helm uninstall $(RELEASE_NAME) -n $(NAMESPACE:="comms") || true

pod-logs: ## 📄 View Helm release logs
	@echo "📄 Viewing Helm release '$(RELEASE_NAME)' logs"
	kubectl logs -n $(NAMESPACE) $(RELEASE_NAME)

pod-logs-follow: ## 📄 Follow Helm release logs
	@echo "📄 Following Helm release '$(RELEASE_NAME)' logs"
	kubectl logs -n $(NAMESPACE) $(RELEASE_NAME) -f
