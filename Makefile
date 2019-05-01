MACHINE=$(shell uname -m)
ACCOUNT=nandyio
IMAGE=button-daemon
VERSION?=0.1
VOLUMES=-v ${PWD}/subscriptions/:/opt/nandy-io/subscriptions/ \
		-v ${PWD}/lib/:/opt/nandy-io/lib/ \
		-v ${PWD}/bin/:/opt/nandy-io/bin/ \
		-v ${PWD}/test/:/opt/nandy-io/test/

.PHONY: build shell test run push create update delete

ifeq ($(MACHINE),armv7l)
DEVICE=--device=/dev/vchiq
endif

build:
	docker build . -f $(MACHINE).Dockerfile -t $(ACCOUNT)/$(IMAGE):$(VERSION)

shell:
	docker run $(DEVICE)-it $(VOLUMES) $(ACCOUNT)/$(IMAGE):$(VERSION) sh

test:
	docker run $(DEVICE) -it $(VOLUMES) $(ACCOUNT)/$(IMAGE):$(VERSION) sh -c "coverage run -m unittest discover -v test && coverage report -m --include lib/service.py"

run:
	docker run $(DEVICE) -it $(VOLUMES) --rm -h $(IMAGE) $(ACCOUNT)/$(IMAGE):$(VERSION)

push:
ifeq ($(MACHINE),armv7l)
	docker push $(ACCOUNT)/$(IMAGE):$(VERSION)
else
	echo "Only push armv7l"
endif

install:
	kubectl create -f kubernetes/daemon.yaml

update:
	kubectl replace -f kubernetes/daemon.yaml

remove:
	-kubectl delete -f kubernetes/daemon.yaml

reset: remove install