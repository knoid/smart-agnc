TRANSLATIONS_IN = $(wildcard resources/i18n/*/LC_MESSAGES/*.po)
TRANSLATIONS = $(patsubst %.po,%.mo,$(TRANSLATIONS_IN))

all: $(TRANSLATIONS)
	mkdir -p src/dist
	gcc -m32 -ggdb -std=gnu99 -I/opt/agns/include -pthread -L/opt/agns/lib \
	-o src/dist/agnc-bind src/c-bind/*.c -l:libagnc.so.1 -l:libagnLogc.so.1

%.mo: %.po
	msgfmt -c -o $@ $^

clean:
	rm -rf src/dist $(TRANSLATIONS)
