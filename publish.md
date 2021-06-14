Make sure the version tag is updated.

Make sure that the working directory is clean.

     source venv/bin/activate
     python setup.py bdist_wheel sdist

Inspect the packages manually

    twine upload dist/*

Tag the git repo.