.PHONY: docker
docker:
	docker/build.sh

.PHONY: check
check:
	@find . -path ./.git -prune -o -type f -name '*.sh' -print | xargs shellcheck
