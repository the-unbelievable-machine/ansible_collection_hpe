.PHONY: .prepare-release-prepare
.prepare-release-prepare: .prepare-release-pre-checks
	@echo '##### TARGET: '$@

	@echo "Ensure changelogs/fragments/release-summary.yml exists  ..."
	@test -e changelogs/fragments/release-summary.yml

	@echo "Create branch release/$(VERSION) if necessary"
	CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
		[[ $${CURRENT_BRANCH} == release/$(VERSION) ]] || git checkout -b release/$(VERSION)

	@echo "Update version"
	sed -i -e 's/^version: .*/version: $(VERSION)/' galaxy.yml


.PHONY: .prepare-release-finalize
.prepare-release-finalize: clean build test

	@echo "Ensure VERSION parameter was supplied"
	@test -n "$(VERSION)"

	@echo "Ensure git is still not dirty - all tracked files are committed (except galaxy.yml)"
	DIRTY=$$(git diff --name-only HEAD  ':(exclude)galaxy.yml' ':(exclude)README.md' ':(exclude)docs/'); test -z "$$DIRTY"

	@echo "Update RELEASE file"
	@echo "$(VERSION)" > RELEASE

	@echo "Generate CHANGELOG"
	$(WITH_VENV) antsibull-changelog release -v --refresh --reload-plugins --update-existing

	git add docs/ changelogs/ galaxy.yml CHANGELOG.rst RELEASE README.md

ifneq ($(NO_COMMIT),true)
	git commit -m "Release $(VERSION)"
ifneq ($(NO_PUSH),true)
	git push -u origin HEAD
else
	@echo "NO_PUSH specified: git push skipped"
endif
else
	@echo "NO_COMMIT specified: git commit and git push skipped"
endif


.PHONY: .prepare-release-pre-checks
.prepare-release-pre-checks: .ensure-git-not-dirty-1
	@echo '##### TARGET: '$@
	@echo "Ensure VERSION parameter was supplied"
	@test -n "$(VERSION)"
	@echo "Ensure VERSION matches regex '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?\$$'"
	@[[ $(VERSION) =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$$ ]] || exit 1

	echo "Ensure git tag $(VERSION) doesn't exist ..."
	git fetch --tags
	@$(eval TAG := $(shell git tag -l $(VERSION)))
	@test -z "$(TAG)"


.PHONY: .ensure-git-not-dirty-%
.ensure-git-not-dirty-%:
	@echo "Ensure git is not dirty - all tracked files are committed"
	DIRTY=$$(git diff --name-only HEAD); test -z "$$DIRTY"
