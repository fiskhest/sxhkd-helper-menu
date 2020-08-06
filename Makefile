SHELL := /bin/bash
SCRIPT = rhkhm
PKGVER = $(shell sed -n "s/^\(.*\)/\1/p" VERSION)

# ANSI terminal colors (see 'man tput') and
# https://linuxtidbits.wordpress.com/2008/08/11/output-color-on-bash-scripts/
#
# Don't use color if there isn't a $TERM environment variable:
ifneq ($(strip $(TERM)),)
	BOLD=$(shell tput bold)
	RED=$(shell tput setaf 1)
	GREEN=$(shell tput setaf 2)
	BLUE=$(shell tput setaf 4)
	MAGENTA=$(shell tput setaf 5)
	UL=$(shell tput sgr 0 1)
	RESET=$(shell tput sgr0 )
endif

# 'sed -i' is not part of the POSIX standard, so it's different for macOS/BSD
ifeq ($(shell uname -s | grep -qiE '(darwin|bsd)'; echo $$?),0)
	SED_INPLACE = sed -i ''
else
	SED_INPLACE = sed -i
endif

help:
	@echo; \
	echo "  $(UL)$(BOLD)$(BLUE)Makefile tasks for $(SCRIPT) v$(PKGVER)$(RESET)"; \
	echo; \
	echo "    $(BOLD)make help$(RESET)                   - ($(GREEN)default$(RESET)) you're looking at it ;-)"; \
	echo; \
	echo "    $(BOLD)make install$(RESET)                - install '$(SCRIPTNAME)' to '$(BINDEST)'"; \
	echo; \
	echo "    $(BOLD)make release VERSION=$(MAGENTA)x.y.z$(RESET)  - create release for '$(SCRIPTNAME)' at version $(MAGENTA)x.y.z$(RESET)"; \
	echo; \
	echo; \
	echo "  For more help, see $(READMEURL)"; \
	echo

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
	$(SED_INPLACE) "s/^\(.*\)/$(VERSION)/p" $^
	git add $^ && git commit -m'Release v$(VERSION)'
	git tag -a v$(VERSION)
	git push --all
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
