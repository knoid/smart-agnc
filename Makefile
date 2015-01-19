TRANSLATIONS_IN = $(wildcard share/locale/*/LC_MESSAGES/*.po)
TRANSLATIONS = $(patsubst %.po,%.mo,$(TRANSLATIONS_IN))
PYC_FILES = $(wildcard src/smart_agnc/*.pyc)
SVG_FILES = $(wildcard share/icons/*/*/*/*.svg)
PNG_FILES = $(patsubst %.svg,%.png,$(SVG_FILES))

all: $(TRANSLATIONS) $(PNG_FILES)
	gcc -m32 -s -ggdb -std=gnu99 -I/opt/agns/include -pthread -L/opt/agns/lib \
	-o bin/sagnc-bind src/c-bind/*.c -l:libagnc.so.1.0.0 -l:libagnLogc.so.1.0.0

clean:
	rm -rf bin/sagnc-bind deb_dist dist MANIFEST smart-agnc-*.tar.gz \
	$(TRANSLATIONS) $(PYC_FILES) $(PNG_FILES)

%.png: %.svg
	rsvg-convert -o $@ $^

%.mo: %.po
	msgfmt -c -o $@ $^
