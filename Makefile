install_python_requirements:
	poetry install

update_python_requirements:
	poetry update

reformat_code:
	black .

publish_package_on_pypi_test:
	rm -rf dist
	poetry build
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	@grep -A 2 "\[testpypi\]" .pypirc | grep "password" | awk '{print $$3}' | xargs -I {} poetry config pypi-token.testpypi {}
	poetry publish --repository testpypi

publish_package_on_pypi:
	rm -rf dist
	poetry build
	@grep -A 2 "\[pypi\]" .pypirc | grep "password" | awk '{print $$3}' | xargs -I {} poetry config pypi-token.pypi {}
	poetry publish
