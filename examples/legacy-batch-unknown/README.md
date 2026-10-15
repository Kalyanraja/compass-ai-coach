# legacy-batch-unknown (SYNTHETIC FIXTURE)

> Synthetic unknown-stack fixture for testing honest fallback. Not from any real
> system. Nothing here is compiled, submitted or run.

Contents:

- `jobs/NIGHTLY.cbl` - COBOL-like batch program that copies records.
- `jobs/run.jcl` - JCL-like job card that would run it.

What the coach should do:

- Report the stack as unknown or unsupported instead of guessing.
- Report build file, test framework, OpenAPI spec, CI and agent instructions as
  not found, rather than inventing them.
- Ask the user how this code is built, tested and deployed.
