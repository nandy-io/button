MACHINE=$(shell uname -m)
ACCOUNT=nandyio
IMAGE=button-daemon
VERSION?=0.1
VOLUMES=-v ${PWD}/lib/:/opt/nandy-io/lib/ \
		-v ${PWD}/bin/:/opt/nandy-io/bin/ \
		-v ${PWD}/test/:/opt/nandy-io/test/
ENVIRONMENT=-e REDIS_HOST=host.docker.internal \
			-e REDIS_PORT=6379 \
			-e REDIS_CHANNEL=nandy.io/chore

.PHONY: build shell test run push install update remove reset tag

ifeq ($(MACHINE),armv7l)
DEVICE=--device=/dev/vchiq
endif

build:
	docker build . -f $(MACHINE).Dockerfile -t $(ACCOUNT)/$(IMAGE):$(VERSION)

shell:
	docker run $(DEVICE)-it $(VOLUMES) $(ENVIRONMENT) $(ACCOUNT)/$(IMAGE):$(VERSION) sh

test:
	docker run $(DEVICE) -it $(VOLUMES) $(ACCOUNT)/$(IMAGE):$(VERSION) sh -c "coverage run -m unittest discover -v test && coverage report -m --include lib/service.py"

run:
	docker run $(DEVICE) -it $(VOLUMES) $(ENVIRONMENT) --rm -h $(IMAGE) $(ACCOUNT)/$(IMAGE):$(VERSION)

push:
ifeq ($(MACHINE),armv7l)
	docker push $(ACCOUNT)/$(IMAGE):$(VERSION)
else
	echo "Only push armv7l"
endif

install:
	kubectl create -f kubernetes/namespace.yaml
	kubectl create -f kubernetes/daemon.yaml

update:
	kubectl replace -f kubernetes/namespace.yaml
	kubectl replace -f kubernetes/daemon.yaml

remove:
	-kubectl delete -f kubernetes/namespace.yaml
	-kubectl delete -f kubernetes/daemon.yaml

reset: remove install

tag:
	-git tag -a "v$(VERSION)" -m "Version $(VERSION)"
	git push origin --tags
