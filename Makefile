.PHONY: docker
docker:
	docker/build.sh

.PHONY: check
check:
	@shellcheck *.sh */*.sh
