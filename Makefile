SHELL := /bin/bash
.PHONY: test-backend test-frontend test build deploy destroy

test-backend:
	@echo "Running backend tests..."
	@cd backend && source .venv/bin/activate && python3 -m pytest --tb=short -q
	@echo "Backend tests passed."

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm run test -- --run
	@echo "Frontend tests passed."

test: test-backend test-frontend

build:
	@echo "Building frontend..."
	@cd frontend && npm run build
	@echo "Frontend build complete."

deploy: test build
	@echo "All tests passed. Deploying..."
	@cd infrastructure && source .venv/bin/activate && cdk deploy --all
	@echo "Deployment complete."

destroy:
	@echo "Destroying all AWS stacks..."
	@cd infrastructure && source .venv/bin/activate && cdk destroy --all
	@echo "All stacks destroyed."
