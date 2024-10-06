# Build for every possible platform (Intel and Apple Silicon)
IMAGE_NAME = demo-python-api
TAG = test

.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install poetry
	poetry install --with test

.PHONY: test
test:
	@echo "Running tests..."
	poetry run pytest --cov

.PHONY: all
all: push

# Build the image for every platform, and load it into the local Docker daemon
.PHONY: build
build:
	docker buildx build -t $(IMAGE_NAME):$(TAG) -f ./deploy/Dockerfile.api --load .

# Build and push the image to the local docker registry
.PHONY: push
push: build
	docker tag ${IMAGE_NAME}:${TAG} localhost:5000/${IMAGE_NAME}:${TAG}
	docker push localhost:5000/${IMAGE_NAME}:${TAG}