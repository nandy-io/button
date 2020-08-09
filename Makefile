VERSION?=0.3
TILT_PORT=26566
.PHONY: up press down tag untag

up:
	kubectx docker-desktop
	-kubectl label node docker-desktop button.nandy.io/button=enabled
	tilt --port $(TILT_PORT) up

press:
	kubectx docker-desktop
	kubens button-nandy-io
	kubectl exec -it $(shell kubectl get pod --no-headers -o custom-columns=":metadata.name") bin/press.py

down:
	kubectx docker-desktop
	tilt down

tag:
	-git tag -a "v$(VERSION)" -m "Version $(VERSION)"
	git push origin --tags

untag:
	-git tag -d "v$(VERSION)"
	git push origin ":refs/tags/v$(VERSION)"
