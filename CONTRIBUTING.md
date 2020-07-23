# How to release


Perform the following actions:
- Make sure all changes are listed in the CHANGELOG file.
- Make sure milestones are checked.
- Make sure all new features/changes are documented.
- Run `make lint` to see code quality diff. If needed update code according to suggestions.
- Update vakt version through all the codebase.
- Push to github (release candidate must be a `master` branch).
- Wait for CI to pass.
- Check code coverage reported to github. Make sure it is sufficient.
- Make sure the local git commit you have checked out is the same as the master commit on github.
- Run `DATABASE_DSN=sqlite:///:memory: make release` to make a release on PyPI.
- Create a release on github (it automatically creates a tag).
