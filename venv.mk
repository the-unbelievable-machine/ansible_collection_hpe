PYTHON_MIN_VERSION = 3.8
PYTHON_VERSION ?= $(shell python3 -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))')

WITH_VENV = source .venv/bin/activate;


version_greater_equal = $(shell if printf '%s\n%s\n' '$(2)' '$(1)' | \
    sort -Ct. -k1,1n -k2,2n ; then echo YES; else echo NO; fi )


VENV_EXITS := $(shell test -d .venv; echo $$? )

.PHONY: venv-create
venv-create:
	@echo '##### TARGET: '$@
ifneq ($(VENV_EXITS),0)
	@echo -n "Verify python version ... required: >= '$(PYTHON_MIN_VERSION)', found: '$(PYTHON_VERSION)': "
	@if [[ $(call version_greater_equal,$(PYTHON_VERSION),$(PYTHON_MIN_VERSION)) == YES ]]; then \
		echo "OK"; else echo "ERROR"; false; fi
	python3 -m venv .venv
	$(WITH_VENV) python -m pip install --timeout 30 --upgrade pip wheel
else
	@echo .venv exists: OK
endif


.venv/updated_requirements.txt: requirements.txt
	@echo '##### TARGET: '$@
	$(WITH_VENV) python -m pip install --timeout 30 -Ur requirements.txt
	touch .venv/updated_requirements.txt


.venv/updated_dev-requirements.txt: dev-requirements.txt
	@echo '##### TARGET: '$@
	$(WITH_VENV) python -m pip install --timeout 30 -Ur dev-requirements.txt
	touch .venv/updated_dev-requirements.txt
