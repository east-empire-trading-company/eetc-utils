install_python_requirements:
	poetry install

update_python_requirements:
	poetry update

update_and_install_python_requirements: update_python_requirements

reformat_code:
	black .

publish_package_on_pypi_test:
	rm -rf dist
	poetry build
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish --repository testpypi

publish_package_on_pypi:
	rm -rf dist
	poetry build
	poetry publish
