Make sure the version number is updated.

Make sure that the working directory is clean.

    source venv/bin/activate
    python -m build

Inspect the packages manually

    twine upload dist/*

Tag the git repo.