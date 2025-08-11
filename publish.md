1. Update the change log:

       CHANGELOG.md

2. Update the version number:

       pyproject.toml

3. Make sure that the working directory is clean.

4. Build:

       uv run --extra build python -m build

5. Inspect the packages manually.

6. Upload:

       uv run --extra build twine upload dist/*

7. Tag the git repo.

8. Read the docs will be updated automatically.
