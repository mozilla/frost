# Checks of GitHub configuration

The code here performs various checks against the configuration of specified
GitHub resources.

At present, the resources queried are organizations & repository branches.

## Common Configuration

* The tests require a GitHub Access Token (PAT) in order to access the
  configuration. The PAT must have read access to the relevant resource.

  The PAT is passed to the code via the environment variable `GH_TOKEN`.

* The tests (currently) extract the list of resources to check by parsing a
  FoxSec specific metadata file. (This will change in the future to be more
  generic.) As such, the local file path to those metadata files must be
  provided.

  The path to the directory is passed to the tests via the environment variable
  `PATH_TO_METADATA`.

# Branch Configuration Checks

Currently implemented checks:
- Are production branches protected?
- Does the protection apply to administrators & owners?
- Is committing restricted to a subset of logins with push access?

# Organization Configuration Checks

Currently implemented checks:
- Does the organization require two factor authentication for all collaborators?
