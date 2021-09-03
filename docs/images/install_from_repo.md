# Install from Repo

To install from the repository first make sure the [prerequisites](#prerequisites) are completed. Then continue on for the technical installation.

## Prerequisites

1. NTC has been given a Github account to add to the appropriate group
2. [Github Personal Access Token created for your account](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)


## Installation from Git

1. Log into the user account used to install Nautobot, if following the Nautobot install documentation it is the `nautobot` user
```
sudo -iu nautobot
```
2. Execute pip install of Device Lifecycle Management Plugin using the HTTPS url and Personal Access Token
```
pip install git+https://github.com/networktocode/nautobot-plugin-device-lifecycle-mgmt.git@v0.1.0
```

**Example Output**
```
nautobot@nautobot-host$ pip install git+https://github.com/networktocode/nautobot-plugin-device-lifecycle-mgmt.git
Collecting git+https://github.com/networktocode/nautobot-plugin-device-lifecycle-mgmt.git
  Cloning https://github.com/networktocode/nautobot-plugin-device-lifecycle-mgmt.git to /tmp/pip-req-build-5p5b8zum
  Running command git clone -q https://github.com/networktocode/nautobot-plugin-device-lifecycle-mgmt.git /tmp/pip-req-build-5p5b8zum
Username for 'https://github.com': jvanderaa
Password for 'https://jvanderaa@github.com':
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
    Preparing wheel metadata ... done
Building wheels for collected packages: nautobot-device-lifecycle-mgmt
  Building wheel for nautobot-device-lifecycle-mgmt (PEP 517) ... done
  Created wheel for nautobot-device-lifecycle-mgmt: filename=nautobot_device_lifecycle_mgmt-0.1.0-py3-none-any.whl size=43330 sha256=44ce2be2bc7c91ebea2a8a70ef65c39d2fe11e2130e1b4539d5c6734fe634ca8
  Stored in directory: /tmp/pip-ephem-wheel-cache-dpwds_ms/wheels/41/a6/d3/7eade40ff7bc4e1fd033f123c289c96d571ea581dc6ec1ea27
Successfully built nautobot-device-lifecycle-mgmt
Installing collected packages: nautobot-device-lifecycle-mgmt
Successfully installed nautobot-device-lifecycle-mgmt-0.1.0
```

Return [Home](../../README.md) to continue the installation process.
