install_python_requirements:
	uv sync

update_python_requirements:
	uv lock --upgrade
	uv sync

reformat_code:
	uv run black .

publish_package_on_pypi_test:
	rm -rf dist
	uv build
	UV_PUBLISH_TOKEN=$$(grep -A 3 "\[testpypi\]" .pypirc | grep "password" | awk '{print $$3}') uv publish --index testpypi

publish_package_on_pypi:
	rm -rf dist
	uv build
	UV_PUBLISH_TOKEN=$$(grep -A 3 "\[pypi\]" .pypirc | grep "password" | awk '{print $$3}') uv publish
