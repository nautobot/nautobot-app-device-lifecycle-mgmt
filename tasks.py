"""Tasks for use with Invoke."""

import os
from invoke import task

PYTHON_VER = os.getenv("PYTHON_VER", "3.8")
NAUTOBOT_VER = os.getenv("NAUTOBOT_VER", "v1.0.0b2")

# Name of the docker image/container
NAME = os.getenv("IMAGE_NAME", "nautobot-eox-notices")
PWD = os.getcwd()

COMPOSE_FILE = "development/docker-compose.yml"
BUILD_NAME = "eox_notices"


# ------------------------------------------------------------------------------
# BUILD
# ------------------------------------------------------------------------------
@task
def build(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER, nocache=False, forcerm=False):
    """Build all docker images.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
        nocache (bool): Do not use cache when building the image
        forcerm (bool): Always remove intermediate containers
    """
    command = (
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} build --build-arg nautobot_ver={nautobot_ver}"
        f" --build-arg python_ver={python_ver}"
    )

    if nocache:
        command += " --no-cache"
    if forcerm:
        command += " --force-rm"

    context.run(command, env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver})


@task
def generate_packages(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Generate all Python packages inside docker and copy the file locally under dist/.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    container_name = f"{BUILD_NAME}_nautobot_package"
    context.run(
        f"docker rm {container_name} || true", env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver}, pty=True,
    )
    context.run(
        f"docker-compose  -f {COMPOSE_FILE} -p {BUILD_NAME} run --name {container_name} -w /source nautobot poetry build",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )
    context.run(
        f"docker cp {container_name}:/source/dist .",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


# ------------------------------------------------------------------------------
# START / STOP / DEBUG
# ------------------------------------------------------------------------------
@task
def debug(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Start Nautobot and its dependencies in debug mode.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    print("Starting Netbox .. ")
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} up",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


@task
def start(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Start Nautobot and its dependencies in detached mode.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    print("Starting Netbox in detached mode.. ")
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} up -d",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


@task
def stop(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Stop Nautobot and its dependencies.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    print("Stopping Netbox .. ")
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} down",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


@task
def restart(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Restart Nautobot and its dependencies.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    print("Restarting Netbox in detached mode.. ")
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} restart",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


@task
def destroy(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Destroy all containers and volumes.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} down",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )
    context.run(
        f"docker volume rm -f {BUILD_NAME}_pgdata_eox_notices",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


# ------------------------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------------------------
@task
def nbshell(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Launch a nbshell session.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot nautobot-server nbshell",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def cli(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Launch a bash shell inside the running Nautobot container.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot bash",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def create_user(context, user="admin", nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Create a new user in django (default: admin), will prompt for password.

    Args:
        context (obj): Used to run specific commands
        user (str): name of the superuser to create
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot nautobot-server createsuperuser --username {user}",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def makemigrations(context, name="", nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run Make Migration in Django.

    Args:
        context (obj): Used to run specific commands
        name (str): Name of the migration to be created
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} up -d postgres",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )

    if name:
        context.run(
            f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot nautobot-server makemigrations --name {name}",
            env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        )
    else:
        context.run(
            f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot nautobot-server makemigrations",
            env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        )

    context.run(
        f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} down",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
    )


# ------------------------------------------------------------------------------
# TESTS / LINTING
# ------------------------------------------------------------------------------
@task
def unittest(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER, keepdb=False, verbosity=1):
    """Run Django unit tests for the plugin.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
        keepdb (bool): Whether to keep the test database for later reuse
        verbosity (int): Verbosity of test output
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    command = f"python manage.py test eox_notices --verbosity={verbosity}"
    if keepdb:
        command += " --keepdb"
    context.run(f'{docker} sh -c "{command}"', env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver}, pty=True)


@task
def pylint(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run pylint code analysis.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    # We exclude the /migrations/ directory since it is autogenerated code
    context.run(
        f"{docker} sh -c \"cd /source && find . -name '*.py' -not -path '*/migrations/*' | "
        'PYTHONPATH=/opt/nautobot/nautobot DJANGO_SETTINGS_MODULE=nautobot.settings xargs pylint"',
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def black(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run black to check that Python files adhere to its style standards.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    context.run(
        f'{docker} sh -c "cd /source && black --check --diff ."',
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def flake8(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """This will run flake8 for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    context.run(
        f"{docker} sh -c \"cd /source && find . -name '*.py' | xargs flake8\"",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def pydocstyle(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run pydocstyle to validate docstring formatting adheres to NTC defined standards.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    # We exclude the /migrations/ directory since it is autogenerated code
    context.run(
        f"{docker} sh -c \"cd /source && find . -name '*.py' -not -path '*/migrations/*' | xargs pydocstyle\"",
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def bandit(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run bandit to validate basic static code security analysis.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    docker = f"docker-compose -f {COMPOSE_FILE} -p {BUILD_NAME} run nautobot"
    context.run(
        f'{docker} sh -c "cd /source && bandit --recursive ./ --configfile .bandit.yml"',
        env={"NAUTOBOT_VER": nautobot_ver, "PYTHON_VER": python_ver},
        pty=True,
    )


@task
def tests(context, nautobot_ver=NAUTOBOT_VER, python_ver=PYTHON_VER):
    """Run all tests for this plugin.

    Args:
        context (obj): Used to run specific commands
        nautobot_ver (str): Nautobot version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    # Sorted loosely from fastest to slowest
    print("Running black...")
    black(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    print("Running flake8...")
    flake8(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    print("Running bandit...")
    bandit(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    print("Running pydocstyle...")
    pydocstyle(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    print("Running pylint...")
    pylint(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    print("Running unit tests...")
    unittest(context, nautobot_ver=nautobot_ver, python_ver=python_ver)
    # print("Running yamllint...")
    # yamllint(context, NAME, python_ver)

    print("All tests have passed!")
