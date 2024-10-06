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

# Start the local docker registry
.PHONY: registry
registry:
	@if [ $$(docker ps -q -f name=registry) ]; then \
		echo "docker registry is running"; \
	elif [ $$(docker ps -a -q -f name=registry) ]; then \
		echo "starting docker registry"; \
		docker start registry; \
	else \
		echo "creating and starting docker registry"; \
		docker run -d -p 5000:5000 --name registry registry:2; \
		docker start registry; \
	fi

# Run some predeploy steps to enable deployment on Docker Desktop Kubernetes
.PHONY: predeploy
predeploy:
	@echo "installing/upgrading ingress-nginx"
	helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace

# Build and push the image to the local docker registry
.PHONY: push
push: registry build
	docker tag ${IMAGE_NAME}:${TAG} localhost:4999/${IMAGE_NAME}:${TAG}
	docker push localhost:5000/${IMAGE_NAME}:${TAG}

# Deploy services to the Docker Desktop Kubernetes cluster
.PHONY: deploy
deploy: push predeploy
	kubectl apply -f ./deploy/01-postgres.yaml
	kubectl apply -f ./deploy/02-api.yaml
