COLLECTION_NAME = unbelievable-hpe
SHELL = /bin/bash

TEST_ARGS ?=

include venv.mk
include prepare-release.mk

.DEFAULT_GOAL := build


.PHONY: all
all: clean build test ## run 'clean', 'build', 'test'


.PHONY: clean
clean: test-clean    ## remove files created by targets 'test', 'build'
	rm -f $(COLLECTION_NAME)-*.tar.gz


.PHONY: clean-all
clean-all: clean    ## like clean, but also removes '.venv'
	rm -rf .venv


.PHONY: setup-env
setup-env: venv venv-dev    ## Setup developer environment (install dev-requirements.txt, enable pre-commit etc)
	@echo '##### TARGET: '$@
	@echo installing pre-commit ...
	@pre-commit install --install-hooks --overwrite
	@echo -e "\nUse '$(WITH_VENV)' to activate python venv"


.PHONY: venv
venv: venv-create .venv/updated_requirements.txt


.PHONY: venv-dev
venv-dev: venv .venv/updated_dev-requirements.txt


.PHONY: build
build: clean venv generate-docs   ## build the collections tar.gz
	@echo '##### TARGET: '$@
	$(WITH_VENV) ansible-galaxy collection build


.PHONY: prepare-release
prepare-release: .prepare-release-pre-checks .prepare-release-prepare .prepare-release-finalize  ## Create a release branch, run build test, generate CHANGELOG and push to origin.


.PHONY: test
test: test-sanity test-unit   ## run all tests


.PHONY: test-sanity
test-sanity: venv test-clean   ## run ansible-test sanity tests in docker
	@echo '##### TARGET: '$@
	$(WITH_VENV) ansible-test sanity --docker -v --color --exclude dev_tools/*.py $(TEST_ARGS)


.PHONY: test-unit
test-unit: venv test-clean
	@echo '##### TARGET: '$@
	$(WITH_VENV) ansible-test units --color --docker --coverage $(TEST_ARGS)


.PHONY: test-clean
test-clean:    ## remove files created by target 'test'
	rm -rf tests/output


.PHONY: generate-docs
generate-docs: venv    ## generate/update collection docs
	@echo '##### TARGET: '$@
ifndef VERSION
	$(WITH_VENV) collection_prep_add_docs -p . -b master
else
	$(WITH_VENV) collection_prep_add_docs -p . -b v$(VERSION)
endif


.PHONY: help
help:    ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
