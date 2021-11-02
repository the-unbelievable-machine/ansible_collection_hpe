# Contribute

## Setup environment

- Create the following directory layout:

  ```text
  └── ansible_collections
      └── unbelievable
          └── hpe    <-- this git repo
  ```

- install `make`
- run `make setup-env`

## make

- Run `make help` to see available targets.
- Target `test` accepts following parameter:
  - `TEST_ARGS`: args passed on to `ansible-test`
- Target `prepare-release` accepts parameter:
  - `TEST_ARGS`: see target `test`.
  - `VERSION`: new version to release.
  - `NO_COMMIT=true`: do not commit new release.
  - `NO_PUSH=true`: do not push new release branch to origin.

## Update / Changes

- Work in a branch / clone repository.
- Create [changelog fragements](https://docs.ansible.com/ansible/latest/community/development_process.html#changelogs-how-to-format)
  in `changelog/fragments`.
  See also [Changelogs for Collections](https://github.com/ansible-community/antsibull-changelog/blob/main/docs/changelogs.rst).
- Run `make test` before create a pull-request.

### Tests

Run `make test` before create a pull-request. This requires `docker`. Running tests may take some time.

> **⚠️ WARNING**  
> Running `make test` sometimes failes with errors like:
>
> ```txt
>  ERROR: Could not find a version that satisfies the requirement cryptography<3.4 (from versions: none)
>  ERROR: No matching distribution found for cryptography<3.4
>  ```
>
> Just try it again.

### Example log fragements

If no ticket exists for your change, just drop the prefix.

- **Inventory**
  `<TICKET>-inventory-<plugin-name>.yml`:

  ```yaml
    ---
    add plugin.inventory:
      - name: oneview
        description: HPE OneView inventory source
  ```

- **Module**
  `<TICKET>-module-<plugin-name>.yml`:

  ```yaml
  ---
  add plugin.module:
    - name: ilo_security_settings
      namespace: unbelievable.hpe
      description: >
        Module to configure iLO security settings. Currently supports
        setting 'SecurityState'.
  ```

- **Playbook**
  `<TICKET>-playbook-<plugin-name>.yml`:

  ```yaml
  ---
  add object.playbook:
    - name: ilo_security_settings
      description: >
        Playbook to configure iLO security settings.
        Currently supports setting 'SecurityState'.
  ```

- **Bugfix**
  `<TICKET>-bugfix-<TICKET-TITLE/DESCRIPTION>.yml`:

  ```yaml
  bugfixes:
  - Module ilo_security_settings - Description of what was fixed.
    (https://github.com/the-unbelievable-machine/ansible_collection_hpe/issues/<TICKET>).
  ```

## Releases

- We are using semantic versioning.
- Make sure all your `changelog fragements` are created.
- Create a `changelogs/fragments/release-summary.yml`:

  ```yml
  release_summary: |
    Some description

    Even more text
  ```

- Run `make prepare-release VERSION=<NEW_VERSION>`. This command will:
  - Verify your VERSION number: `<major>.<minor>.<bugfix><suffix>`.
    - `<major>`, `<minor>` and `<bugfix>` must be numbers.
    - `<suffix>` is optional, but it must start with '-' and must only contain alpha-numeric
      characters ('-[a-zA-Z0-9]+')
  - Verify no git tag `<VERSION>` exists.
  - Verify all git tracked files are committed - your repository is not dirty.
  - Verify `changelogs/fragments/release-summary.yml` exists
  - Run `make clean build test`. NOTICE: running `test` requires `docker` and may take some time.
  - Verify again that all git tracked files are committed - your repository is not dirty.
  - Create branch `release/<VERSION>` if not already in it.
  - Update version number in `galaxy.yml`.
  - Generate `CHANGELOG.rst` file using `antsibull-changelog`
  - Add following files to git:
    - changelogs/
    - CHANGELOG.rst
    - galaxy.yml
  - Run `git commit -m "Release v<VERSION>"` unless parameter `NO_COMMIT=true` is used.
  - Run `git push -u origin HEAD` unless parameter `NO_PUSH=true` is used.

- Create a pull-request via GitHub.
  - Only fast-forward pull requests are aloud.
  - Pull requests to master must have only on commit.
  - Commit message should be in english and follow the layout:

    ```txt
    <TICKET>: Short description

    Some more description
    ```

  This will trigger GitHub workflow `Pull request to master`.

- If workflow `Pull request to master` succeeded, merging the request into branch `master` will trigger
  another GitHub workflow: `Build new release`. This workflow will run checks and create a new tag `v<VERSION>`
  if all checks succeeded.

> **🗨️ HINT**  
> In case `make prepare-release` fails, you can:
>
> - fix things in the `release/XXX` branch.
> - commit your changes.
> - Rebase your branch so that only one commit remains.
> - pickup release process by running `make .prepare-release-finalize VERSION=<NEW_VERSION>`.
