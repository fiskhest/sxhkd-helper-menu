SHELL := /bin/bash

# 'sed -i' is not part of the POSIX standard, so it's different for macOS/BSD
ifeq ($(shell uname -s | grep -qiE '(darwin|bsd)'; echo $$?),0)
	SED_INPLACE = sed -i ''
else
	SED_INPLACE = sed -i
endif

all: tests build publish

# include tools/config.mk

.PHONY: all tests build publish release

tests:
	bash tests/keychain_contains_multiple_spaces.sh

build:
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

install:
	python setup.py install

# get VERSION from the environment/command line; use it to update the version
# of the script and create a Git release commit + tag
release: VERSION
ifeq ($(VERSION),)
	@echo >&2; \
	echo "  $(UL)$(BOLD)$(RED)OH NOES!$(RESET)"; \
	echo >&2; \
	echo "  Expected a value for VERSION. Try again like this:"; \
	echo >&2; \
	echo "      $(BOLD)make release VERSION=x.y.z$(RESET)" >&2; \
	echo >&2
	@false
else
	@if ! [[ $(VERSION) =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$$ ]]; then \
		echo "(!!) $(BOLD)$(RED)ERROR$(RESET) - bad version; expected x.y[.z], where x, y, and z are all integers." >&2; \
		exit 1; \
	fi
	#@if git status --porcelain | grep .; then \
	#	echo "(!!) $(BOLD)$(RED)ERROR$(RESET) - Git working tree is dirty; commit changes and try again." >&2; \
	#	exit 1; \
	#fi
	@if git tag | grep v$(VERSION); then \
		echo "(!!) $(BOLD)$(RED)ERROR$(RESET) - release v$(VERSION) already exists." >&2; \
		exit 1; \
	fi
	# replace version string in all target dependencies
	@# '$^' below means "the names of all the prerequisites"
	$(SED_INPLACE) "s/^\(VERSION=\)'\(.*\)'/\1'$(VERSION)'/" $^
	git add $^ && git commit -m'Release v$(VERSION)'
	git tag -a v$(VERSION)
	git push --tags
	@echo; \
	echo "  $(UL)$(BOLD)$(BLUE)SUPER!$(RESET)"; \
	echo; \
	echo "  Updated '$(SCRIPT)' v$(PKGVER) to v$(VERSION)"; \
	echo; \
	echo "  It would be a good idea now to:"; \
	echo; \
	echo "      $(BOLD)make install$(RESET)"; \
	echo; \
	echo "  to update the installed script."; \
	echo
endif

#%_release:
#	git tag -a $(bash tests/get_release.sh $@)
#	git push --follow-tags
	
