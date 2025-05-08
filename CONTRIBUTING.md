# Contributing to nipanel-python

Contributions to nipanel-python are welcome from all!

nipanel-python is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/<reponame>/).

nipanel-python follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

Please remember to sign off your commits (e.g., by using `git commit -s` if you
are using the command line client). This amends your git commit message with a line
of the form `Signed-off-by: Name Lastname <name.lastmail@emailaddress.com>`. Please
include all authors of any given commit into the commit message with a
`Signed-off-by` line. This indicates that you have read and signed the Developer
Certificate of Origin (see below) and are able to legally submit your code to
this repository.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

# Getting Started

This is the command to generate the files in /src/ni/pythonpanel/v1/:
`poetry run python -m grpc_tools.protoc --proto_path=protos --python_out=src/ --grpc_python_out=src/ --mypy_out=src/ --mypy_grpc_out=src/ ni/pythonpanel/v1/python_panel_service.proto`

# Testing

## Simple development loop

```
# Create a new branch
git fetch
git switch --create users/{username}/{branch-purpose} origin/main

# Install the project dependencies
poetry install

# ✍ Make source changes

# Run the analyzers -- see files in .github/workflows for details
poetry run nps lint
poetry run mypy
poetry run bandit -c pyproject.toml -r src/nipanel

# Run the tests
poetry run pytest -v
```

# Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/<reponame>/blob/main/LICENSE)
for details about how \<reponame\> is licensed.
