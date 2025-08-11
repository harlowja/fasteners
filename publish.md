1. Update the change log:

       CHANGELOG.md

2. Update the version number:

       pyproject.toml
       fasteners/version.py

3. Make sure that the working directory is clean.

4. Build:

       uv run --group build python -m build

5. Inspect the packages manually.

6. Upload:

       uv run --group build twine upload dist/*

7. Tag the git repo.

8. Read the docs will be updated automatically.
