# Minimal makefile for Sphinx documentation
#

# To regenerate the apidoc:
#   rm api/niimpy.*
#   sphinx-apidoc -e -o api/ ../niimpy/

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python3 -m sphinx
SPHINXPROJ    = Niimpy
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Regenerate apidocs, needs to be re-run when new modules are made (or
# run as part of doc build process)
apidoc:
	rm api/niimpy.*
	sphinx-apidoc --force -e -H "niimpy API docs" -o api/ ../niimpy/ '../niimpy*/test_*'
