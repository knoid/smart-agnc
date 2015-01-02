all:
	mkdir -p dist
	gcc -m32 -ggdb -std=gnu99 -I/opt/agns/include -pthread -L/opt/agns/lib \
	-o dist/agnc-bind c-bind/*.c -lagnc -lagnLogc

clean:
	rm -rf dist
