COURSE=		cse.30124.fa24
WWWROOT=	docs
COMMON= 	scripts/yasb.py templates/base.tmpl $(wildcard static/yaml/*.yaml)
RSYNC_FLAGS= 	-rv --copy-links --progress --exclude="*.swp" --exclude="*.yaml" --size-only
YAML=		$(shell ls pages/*.yaml)
HTML= 		$(YAML:.yaml=.html)

all:		$(HTML)

%.html:		%.yaml $(COMMON)
	./scripts/yasb.py $< > $@

build:		$(HTML)
	mkdir -p $(WWWROOT)/static
	cp -frv pages/*.html		$(WWWROOT)/.
	cp -frv static/*		$(WWWROOT)/static/.
	cp -frv static/ico/favicon.ico	$(WWWROOT)/.

install:	build
	lftp -c "open www3ftps.nd.edu; mirror -n -e -R -L $(WWWROOT) www/teaching/$(COURSE)"

push:
	git checkout docs && git pull --rebase && git push

clean:
	rm -f $(HTML)
