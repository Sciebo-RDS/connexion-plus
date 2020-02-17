deps:
	python3 -m pip install --user --upgrade setuptools wheel
	python3 -m pip install --user --upgrade twine

build: deps
	python3 setup.py sdist bdist_wheel

upload: build
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*