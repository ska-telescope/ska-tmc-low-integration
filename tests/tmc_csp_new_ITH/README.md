# TMC-CSP Pairwise integration tests (implemented using the new ITH)

This folder contains a set of TMC-CSP (in MID) pairwise integration tests
implemented using the new
[Integration Test Harness (ITH)](https://developer.skao.int/projects/ska-integration-test-harness/en/latest/?badge=latest).

## Overview

This folder contains a set of TMC-CSP pairwise integration tests, somehow
redundant with [tests/tmc_csp](../tmc_csp/) but which differ for the following
aspects:

- they are implemented using the new ITH, independently from the
 set of modules contained in [tests/resources](../resources/) (the previous
 TMC test harness);
- they implement a different set of scenarios, defined in 
  [features](features/) and grouped in just two feature;
- they focus on systematically covering all the subarray `obsState`
  transactions from a quiescent state to a quiescent state (with an
  eventual passage through the intermediate transient state); 
- they follows a structured schema in the naming conventions and
  they are designed thinking about the re-use of the steps (especially
  the re-use of the `given` steps).

## Folder content

The folder contains the following files and subfolders.

- [bdd-steps-doc](bdd-steps-doc/): the folder containing the
  auto-generated markdown test documentation. You can use this as a reference to
  understand what each test is doing. This documentation is generated
  extracting all the necessary information from the feature files
  and from the steps implementation. The documentation is generated
  using the `document_steps.py` support script, called through the
  `make bdd-steps-doc` command. For more details, see the
  [Makefile](../../Makefile) and the
  [support scripts README](../../helper_scripts/README.md).
- [features](features/): the folder containing the Gherkin feature files
  implementing the scenarios. Some important notes about the features:
  - the main feature are two: one for covering the "regular" subarray
    transactions (assign resources, configure, scan, etc.)
    and one for the "exceptional" transactions (i.e., the ones regarding
    the `Abort` and `Restart` commands);
  - all the scenarios implement happy paths, i.e., they are designed
    to cover the nominal behavior of the system;
  - all the scenarios share some `Background` steps, which essentially
    initialize the system in a `ON` telescope state and in a `EMPTY`
    subarray state;
  - the scenarios are decorated with one or more - not yet used - tags
    that indicates the covered transactions;
  - a third, still incomplete feature is added to cover some transactions
    related to the `telescopeState`, but their implementation is still
    naive and may be subject to changes.
- [specifications](specifications/): the folder containing a some scripts and
  some feature files drafts. They are not used in the current test
  implementation but they are the code and the draft used to generate
  the initial version of the features starting from the `obsState` state
  machine graph. The content of this folder is probably not needed
  to understand the current test implementation.
- [utils](utils/): some utility code, like the extensions of the ITH
  input classes (to access the [test data](../data/) in an easier way).
- [conftest.py](conftest.py): the `pytest` configuration file. Right now it
  contains the fixtures to
  [initialize the ITH](https://developer.skao.int/projects/ska-integration-test-harness/en/latest/getting_started.html)
  and the various other involved tools (e.g., `TangoEventTracer`, fixtures
  to keep track of the states and the commands to facilitate the
  steps generalization, etc.). At the moment, also some generalized steps
  are implemented here.
- [test_abort.py](test_abort.py) and
  [test_command_triggered.py](test_command_triggered.py):
  the two test files containing the implementation of the test cases.
- [test_telescope_state.py](test_telescope_state.py): the test file
  containing the implementation of the test cases related to the
  `telescopeState` transactions (still naive and subject to changes).
- [test_harness_config.yaml](test_harness_config.yaml): the configuration
  file for the ITH. It contains the expected device names for TMC, CSP,
  SDP and the Dishes and it specifies that the ITH expects TMC and CSP
  to be production deployments, while instead SDP and Dishes are
  expected to be emulated.

## How to run the tests

A new marker called `tmc_csp_new_ITH` has been introduced to
run the tests.

To run the tests:

1. you setup the pods, ensuring CSP and TMC are in production mode:

    ```bash
    make k8s-install-charts CSP_SIMULATION_ENABLED=false
    ```
   and you ensure to wait the deployment is completed:

    ```bash
    make k8s-wait
    ```

2. you run the new tests specifying the marker and the fact you
   want CSP to not be emulated:

    ```bash
    make k8s-test CSP_SIMULATION_ENABLED=false MARK=tmc_csp_new_ITH
    ```

Some further, maybe useful `Makefile` variables are:

- `PYTHON_TEST_NAME="..."` to use the `-k` option of `pytest` to
  filter the tests by python name;
- `EXIT_AT_FAIL=false` to not exit at the first failure.

## New tests in the pipeline, Jira-Xray and test documentation

The new tests are executed in the pipeline and their results are pushed
on Jira-Xray (associated to the test plan `XTP-62547`).

The pipeline is defined in
[gitlab_ci/.gitlab-ci-tmc-csp-new-ith.yml](../../gitlab_ci/.gitlab-ci-tmc-csp-new-ith.yml),
by default it sets `EXIT_AT_FAIL=false`.

The pipeline is also set up to make use of the new
[support scripts](../../helper_scripts/README.md). In particular:

- thanks to
  [pytest-bdd-report](https://github.com/mattiamonti/pytest-bdd-report)
  we generate a nice HTML report of the test execution;
- a link to that report (currently stored in the job artifacts) is
  published in the Jira ticket associated with the current CI JOB, through
  a hook that after executing `ska-ser-xray` calls the support script
  `publish_test_report.py`;
- thanks to the `document_steps.py` support script you can generate
  (manually) a markdown documentation of the tests (generated through
  `make bdd-steps-doc` and currently stored
  in [tests/tmc_csp_new_ITH/bdd-steps-doc/](bdd-steps-doc/index.md));
  a link to that documentation is also published in the Jira ticket
  associated with the current CI JOB by the same script, but that
  option is enabled only if the `ADD_DOCS_LINK_TO_JIRA` flag is set to
  `ADD_DOCS_LINK_TO_JIRA=true` in the pipeline configuration (which
  is done just for this CI JOB).

See the [Makefile](../../Makefile) for the details of those integrations.




