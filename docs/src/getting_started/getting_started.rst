Getting started
===============

This page contains instructions for software developers who want to get
started with usage and development of the TMC integration repository.

Background
----------
Detailed information on how the SKA Software development
community works is available at the `SKA software developer portal <https://developer.skao.int/en/latest/>`_.
There you will find guidelines, policies, standards and a range of other
documentation.

Set up your development environment
-----------------------------------
This project is structured to use k8s for development and testing so that the build environment, test environment and test results are all completely reproducible and are independent of host environment. It uses ``make`` to provide a consistent UI (run ``make help`` for targets documentation).

Install minikube
^^^^^^^^^^^^^^^^

You will need to install `minikube` or equivalent k8s installation in order to set up your test environment. You can follow the instruction `here <https://gitlab.com/ska-telescope/sdi/deploy-minikube/>`_:
::
git clone git@gitlab.com:ska-telescope/sdi/deploy-minikube.git
cd deploy-minikube
make all
eval $(minikube docker-env)

*Please note that the command `eval $(minikube docker-env)` will point your local docker client at the docker-in-docker for minikube. Use this only for building the docker image and another shell for other work.*

How to Use
^^^^^^^^^^

Clone this repo:
::
git clone https://gitlab.com/ska-telescope/ska-tmc-low-integration.git
cd ska-tmc-low-integration


To deploy the pods:
::
make k8s-install-chart

To test the integration test cases:
::
make k8s-test

To uninstall the pods:
::
make k8s-uninstall-chart

To watch the pods, services status:
::
make k8s-watch


