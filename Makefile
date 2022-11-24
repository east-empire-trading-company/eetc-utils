install_python_requirements:
	pip install pip-tools
	pip install -r requirements.txt

update_python_requirements:
	pip install pip-tools
	pip-compile --upgrade

update_and_install_python_requirements: update_python_requirements install_python_requirements

reformat_code:
	black .

publish_package_on_pypi_test:
	rm -rf dist
	python -m build
	python -m twine upload --repository testpypi dist/*

publish_package_on_pypi:
	rm -rf dist
	python -m build
	python -m twine upload --repository pypi dist/*
