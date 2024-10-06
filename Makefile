# Build for every possible platform (Intel and Apple Silicon)
IMAGE_NAME = demo-python-api
TAG = test

.PHONY: all
all: build

# Build the image for every platform, and load it into the local Docker daemon
.PHONY: build
build:
	docker buildx build -t $(IMAGE_NAME):$(TAG) -f ./deploy/Dockerfile.api --load ./api
