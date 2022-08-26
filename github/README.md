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

# Implemented Checks

## Branch Configuration Checks

Currently implemented checks:
- Are production branches protected?
- Does the protection apply to administrators & owners?
- Is committing restricted to a subset of logins with push access?

## Organization Configuration Checks

Currently implemented checks:
- Does the organization require two factor authentication for all collaborators?

# Development Notes

- These tests interact with GitHub using the [GraphQL api][gql-api] (aka v4) to
  perform as many of the queries as possible. It is more concise than the [REST
  api][rest-api] (aka v3), and appears more performant as well. At this time,
  the v4 api is not as complete as v3, so some v3 queries may be needed in the
  future.

- The chosen GraphQL library is [Simple GraphQL Client][sgqlc], which includes support
  for the autogeneration of the required schema file for the relevant API --
  `github_schema.py` in our case. That file is used by the library, and only
  needs to be changed if our needs change. (GraphQL schemas are usually backward
  compatible, so there is no need to "always update".) See the sgqlc
  documentation for how to use the [code generator][sgqlc-cg].


<!-- References -->

[gql-api]: https://docs.github.com/en/free-pro-team@latest/graphql
[rest-api]: https://docs.github.com/en/free-pro-team@latest/rest
[sgqlc]: https://github.com/profusion/sgqlc
[sgqlc-cg]: https://github.com/profusion/sgqlc#code-generator
