"""Tasks for use with Invoke."""

import os
from invoke import task

PYTHON_VER = os.getenv("PYTHON_VER", "3.8")
NAUTOBOT_VER = os.getenv("NAUTOBOT_VER", "v1.0.1")

# Name of the docker image/container
NAME = os.getenv("IMAGE_NAME", "nautobot-eox-notices")
PWD = os.getcwd()

BUILD_NAME = "eox_notices"
COMPOSE_DIR = os.path.join(os.path.dirname(__file__), "development/")
COMPOSE_FILE = os.path.join(COMPOSE_DIR, "docker-compose.yml")
COMPOSE_OVERRIDE_FILE = os.path.join(COMPOSE_DIR, "docker-compose.override.yml")
COMPOSE_COMMAND = f'docker-compose --project-directory "{COMPOSE_DIR}" -f "{COMPOSE_FILE}" -p "{BUILD_NAME}"'

if os.path.isfile(COMPOSE_OVERRIDE_FILE):
    COMPOSE_COMMAND += f' -f "{COMPOSE_OVERRIDE_FILE}"'


def docker_compose(context, command, **kwargs):
    """Helper function for running a specific docker-compose command with all appropriate parameters and environment.

    Args:
        context (obj): Used to run specific commands
        command (str): Command string to append to the "docker-compose ..." command, such as "build", "up", etc.
        **kwargs: Passed through to the context.run() call.
    """
    default_env = {"NAUTOBOT_VER": NAUTOBOT_VER, "PYTHON_VER": PYTHON_VER}
    # If not supplied, add defaults
    if "env" not in kwargs:
        kwargs["env"] = default_env
    else:
        # Keep environments task passed in but default NAUTOBOT_VER and PYTHON_VER
        # as they're managing globally and not per task
        kwargs["env"].update(default_env)
    print(f'Running docker-compose command "{command}"')
    return context.run(f"{COMPOSE_COMMAND} {command}", **kwargs)


# ------------------------------------------------------------------------------
# BUILD
# ------------------------------------------------------------------------------
@task
def build(context, nocache=False, forcerm=False):
    """Build all docker images."""
    command = f"build --build-arg nautobot_ver={NAUTOBOT_VER} --build-arg python_ver={PYTHON_VER}"

    if nocache:
        command += " --no-cache"
    if forcerm:
        command += " --force-rm"

    docker_compose(context, command)


@task
def generate_packages(context):
    """Generate all Python packages inside docker and copy the file locally under dist/."""
    container_name = f"{BUILD_NAME}_nautobot_package"
    context.run(
        f"docker rm {container_name} || true", env={"NAUTOBOT_VER": NAUTOBOT_VER, "PYTHON_VER": PYTHON_VER}, pty=True,
    )
    context.run(
        f"docker-compose  -f {COMPOSE_FILE} -p {BUILD_NAME} run --name {container_name} -w /source nautobot poetry build",
        env={"NAUTOBOT_VER": NAUTOBOT_VER, "PYTHON_VER": PYTHON_VER},
    )
    context.run(
        f"docker cp {container_name}:/source/dist .",
        env={"NAUTOBOT_VER": NAUTOBOT_VER, "PYTHON_VER": PYTHON_VER},
        pty=True,
    )


# ------------------------------------------------------------------------------
# START / STOP / DEBUG
# ------------------------------------------------------------------------------
@task
def debug(context):
    """Start Nautobot and its dependencies in debug mode."""
    print("Starting Netbox .. ")
    docker_compose(context, "up")


@task
def start(context):
    """Start Nautobot and its dependencies in detached mode."""
    print("Starting Netbox in detached mode.. ")
    docker_compose(context, "up -d")


@task
def stop(context):
    """Stop Nautobot and its dependencies."""
    print("Stopping Netbox .. ")
    docker_compose(context, "down")


@task
def restart(context):
    """Restart Nautobot and its dependencies."""
    print("Restarting Netbox in detached mode.. ")
    docker_compose(context, "restart")


@task
def destroy(context):
    """Destroy all containers and volumes."""
    docker_compose(context, "down")
    context.run(
        f"docker volume rm -f {BUILD_NAME}_pgdata_eox_notices",
        env={"NAUTOBOT_VER": NAUTOBOT_VER, "PYTHON_VER": PYTHON_VER},
    )


# ------------------------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------------------------
@task
def nbshell(context):
    """Launch a nbshell session."""
    docker_compose(
        context, "run --entrypoint 'nautobot-server nbshell' nautobot", pty=True,
    )


@task
def cli(context):
    """Launch a bash shell inside the running Nautobot container."""
    docker_compose(
        context, "run --entrypoint bash nautobot", pty=True,
    )


@task
def create_user(context, user="admin"):
    """Create a new user in django (default: admin), will prompt for password."""
    print(f"Starting user creation for user {user}")
    docker_compose(
        context, f"run --entrypoint 'nautobot-server createsuperuser --username {user}' nautobot", pty=True,
    )


@task
def makemigrations(context, name=""):
    """Run Make Migration in Django."""
    docker_compose(context, "up -d postgres")

    entrypoint = "nautobot-server makemigrations"
    if name:
        entrypoint += f" --name {name}"
    command = f"run --entrypoint '{entrypoint}' nautobot"

    # Run migrations
    docker_compose(context, command)
    # Spin down the environment after migrations have been created
    docker_compose(context, "down")


# ------------------------------------------------------------------------------
# TESTS / LINTING
# ------------------------------------------------------------------------------
@task
def unittest(context, keepdb=False, verbosity=1):
    """Run Django unit tests for the plugin."""
    entrypoint = f"nautobot-server test eox_notices --verbosity={verbosity}"
    if keepdb:
        entrypoint += " --keepdb"
    command = f"run --entrypoint '{entrypoint}' nautobot"
    docker_compose(context, command, pty=True)


@task
def pylint(context):
    """Run pylint code analysis."""
    entrypoint = (
        'pylint --init-hook "import nautobot; nautobot.setup()" --rcfile /source/pyproject.toml /source/eox_notices'
    )
    command = f"run --entrypoint '{entrypoint}' nautobot"
    docker_compose(
        context, command, pty=True,
    )


@task
def black(context):
    """Run black to check that Python files adhere to its style standards."""
    command = "run --entrypoint 'black --check --diff /source' nautobot"
    docker_compose(context, command, pty=True)


@task
def flake8(context):
    """This will run flake8 for the specified name and Python version."""
    command = "run --entrypoint 'flake8 --config /source/.flake8 /source' nautobot"
    docker_compose(context, command, pty=True)


@task
def pydocstyle(context):
    """Run pydocstyle to validate docstring formatting adheres to NTC defined standards."""
    # We exclude the /migrations/ directory since it is autogenerated code
    command = 'run --entrypoint "pydocstyle --config=/source/.pydocstyle.ini /source/" nautobot'
    docker_compose(context, command, pty=True)


@task
def bandit(context):
    """Run bandit to validate basic static code security analysis."""
    command = "run --entrypoint 'bandit --recursive /source --configfile /source/.bandit.yml' nautobot"
    docker_compose(context, command, pty=True)


@task
def tests(context):
    """Run all tests for this plugin."""
    # Sorted loosely from fastest to slowest
    print("Running black...")
    black(context)
    print("Running flake8...")
    flake8(context)
    print("Running bandit...")
    bandit(context)
    print("Running pydocstyle...")
    pydocstyle(context)
    print("Running pylint...")
    # TODO (mik): Uncomment and fix legit errors once all unittests are written and passing.
    # pylint(context)
    # print("Running unit tests...")
    unittest(context)

    print("All tests have passed!")
