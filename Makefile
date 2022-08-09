PROJECT := cads_toolbox
CONDA := conda
CONDAFLAGS :=
COV_REPORT := html

default: qa unit-tests type-check

qa:
	pre-commit run --all-files

unit-tests:
	python -m pytest -vv --cov=. --cov-report=$(COV_REPORT)

type-check:
	python -m mypy .

conda-env-update:
	$(CONDA) env update $(CONDAFLAGS) -f environment.yml

docker-build:
	docker build -t $(PROJECT) .

docker-run:
	docker run --rm -ti -v $(PWD):/srv $(PROJECT)

template-update:
	pre-commit run --all-files cruft -c .pre-commit-config-weekly.yaml

docs-build:
	cd docs && rm -fr _api && make clean && make html

# DO NOT EDIT ABOVE THIS LINE, ADD COMMANDS BELOW

doc-tests:
	python -m pytest -vv --cov=. --cov-report=$(COV_REPORT) --doctest-glob="*.md" README.md

REPOSITORIES := \
	../cacholote \
	../cads-api-client \
	../cgul \
	../teal

# the commands below are executed once to setup the development environment,
# repositories are cloned into sibling folders

git-clone-all: $(REPOSITORIES)

../cacholote:
	git clone git@github.com:bopen/cacholote.git $@

../%:
	git clone git@github.com:ecmwf-projects/$*.git $@

pip-install-all: $(REPOSITORIES)
	@for repo in $^; do	\
		pip install --no-deps -e $(CURDIR)/$$repo; \
	done;
	pip install --no-deps -e $(CURDIR)

git-pull-all: $(REPOSITORIES)
	@for repo in $^; do	\
		git -C $(CURDIR)/$$repo pull; \
	done;
