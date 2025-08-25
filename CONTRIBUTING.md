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

# Testing

## Simple development loop

```
# Create a new branch
git fetch
git switch --create users/{username}/{branch-purpose} origin/main

# Install the project dependencies
poetry install --extras docs

# ✍ Make source changes

# Run the analyzers -- see files in .github/workflows for details
poetry run ni-python-styleguide lint
poetry run mypy
poetry run bandit -c pyproject.toml -r src/nipanel

# Apply safe fixes
poetry run ni-python-styleguide fix

# Run the tests
poetry run pytest -v

# Build and inspect the documentation
poetry run sphinx-build docs docs/_build --builder html --fail-on-warning
start docs\_build\index.html
```

## Running examples

1. Run the **PythonPanelService** (not part of this repo, provided seperately)
2. `poetry install --extras examples` to get the dependencies needed for the examples
3. Run the examples with these command(s):
    - `poetry run python examples/hello/hello.py`
    - `poetry run python examples/all_types/all_types.py`
    - `poetry run python examples/simple_graph/simple_graph.py`
    - `poetry run python examples/nidaqmx/nidaqmx_continuous_analog_input.py` (requires real or simulated devices)
4. Open http://localhost:42001/panel-service/ in your browser, which will show all running panels

# Debugging on the streamlit side

Debugging the measurement script can be done using standard Python debugging
techniques. However, debugging the Streamlit script—or any code invoked by the
Streamlit script—is more complex because it runs in a separate process launched
by the PythonPanelServer. To debug the Streamlit script, you can use debugpy to
attach the Visual Studio Code debugger as follows:

## Instrument Streamlit script to debug

To enable debugpy debugging, include this code in your streamlit script:

```python
import debugpy  # type: ignore

try:
    debugpy.listen(("localhost", 5678))
    debugpy.wait_for_client() 
except RuntimeError as e:
    if "debugpy.listen() has already been called on this process" not in str(e):
        raise
```

The `debugpy.listen()` function opens a port that allows the debugger to attach
to the running process. You can specify any available port, as long as it
matches the port configured in the launch.json file shown below. Since calling
listen() more than once will raise an exception, it is wrapped in a try block to
prevent the script from crashing if it is rerun.

The `debugpy.wait_for_client()` function pauses script execution until the
debugger is attached. This is helpful if you need to debug initialization code,
but you can omit this line if it is not required.

The `import debugpy` statement includes a type suppression comment to satisfy mypy.

## Add debugpy configuration in launch.json 

You will also need this configuration in your launch.json:

```json
        {
            "name": "Attach to Streamlit at localhost:5678",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "justMyCode": false
        }
```

After running your measurement script and allowing the PythonPanelServer to
launch Streamlit with your Streamlit script, you can attach the debugger by
clicking the **Attach to Streamlit at localhost:5678** button in the VS Code
**Run and Debug** tab. Once attached, you can set breakpoints and use all
standard debugging features in your Streamlit script, as well as in any nipanel
code invoked by the Streamlit script.

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
