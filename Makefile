.PHONY: docker
docker:
	docker/build.sh

.PHONY: check
check:
	@find . -type f -name '*.sh' | xargs shellcheck
