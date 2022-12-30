# Contributing to the App

The project is packaged with a light [development environment](dev_environment.md) based on `docker-compose` to help with the local development of the project and to run tests.

The project is following Network to Code software development guidelines and is leveraging the following:

- Black, Pylint, Bandit, flake8, and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

Documentation is built using [mkdocs](https://www.mkdocs.org/). The [Docker based development environment](dev_environment.md#docker-development-environment) automatically starts a container hosting a live version of the documentation website on [http://localhost:8001](http://localhost:8001) that auto-refreshes when you make any changes to your local files.

## Branching Policy

Device Lifecycle Plugin leverages a feature and develop branching strategy.  The default branch has been changed to the `develop` branch, and all feature branches should source from it.  Once a feature has been merged back into develop, it will be considered to merge into main along with other feature branches - which will ultimately lead to the next release.

## Release Policy

New versions of the Device Lifecycle plugin are based on the most recent PR's that have been merged into the develop branch.  A release can contain major or minor changes, as well as bug patches.  The product owner, and tech lead are responsible for determining when a group of PR's will be tagged and released.  In general, the maintainers follow the semantic release philosophy of Major, Minor, Patch release determination.
