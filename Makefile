#
# Development by Carl J. Nobile
#

PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
#DOCS_DIR	= $(PREFIX)/docs
LOGS_DIR	= $(PREFIX)/central/logs
TODAY		= $(shell date +"%Y-%m-%d_%H%M")

#----------------------------------------------------------------------
all	: tar

#----------------------------------------------------------------------
tar	: clean
	@(cd ..; tar -czvf $(PACKAGE_DIR).tar.gz --exclude=".git" \
          --exclude=".gitignore" $(PACKAGE_DIR))

tests	:
	@(export PYTHONPATH=$(PREFIX); \
         python motors/pololu/tests/test_qik2s9v1.py; \
        )

#----------------------------------------------------------------------

clean	:
	$(shell cleanDirs.sh clean)
