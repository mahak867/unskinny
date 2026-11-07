all: cad sim test
cad:
	python3 cad/build.py
sim:
	python3 sim/plots.py
test:
	python3 -m pytest -q tests
clean:
	rm -rf out/*
.PHONY: all cad sim test clean
