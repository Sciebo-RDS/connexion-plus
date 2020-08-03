init:
	python3 -m pip install --user --upgrade pip
	python3 -m pip install --user --upgrade setuptools wheel
	python3 -m pip install --user --upgrade twine

upload:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -r dist src/*.egg-info build .coverage coverage.xml .pytest_cache *.egg-info