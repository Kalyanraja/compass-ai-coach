---
description: 'C#/.NET conventions and xUnit/NUnit/MSTest test rules.'
applyTo: '**/*.cs,**/*.csproj'
---
<!-- practice: P3 test-first-acceptance -->

# C# / .NET rules

## Code
- Target {{DOTNET_VERSION}}. Enable nullable reference types; do not suppress warnings with `!` without a comment explaining why.
- Use `async`/`await` end to end. No `.Result` or `.Wait()`. Pass `CancellationToken` through I/O paths.
- Constructor dependency injection. Register lifetimes deliberately (singleton services must be thread-safe).
- Throw specific exceptions; never `catch (Exception) { }`. Use `ArgumentNullException.ThrowIfNull` for guards.
- `using`/`await using` for disposables.
- Data access: parameterized queries (`SqlParameter`, Dapper parameters, EF Core LINQ). Never interpolate input into SQL; avoid `FromSqlRaw` with input.
- Structured logging (`logger.LogInformation("Saved order {OrderId}", id)`); never log secrets or personal data.

## Tests
- Framework: {{CSHARP_TEST_FRAMEWORK}} (xUnit preferred). Name tests `Method_Scenario_ExpectedResult`.
- xUnit: `[Fact]` for single cases, `[Theory]` + `[InlineData]`/`[MemberData]` for tables. Constructor for setup, `IDisposable`/`IAsyncLifetime` for teardown.
- Assert one behavior. Use `Assert.Throws<T>`/`Assert.ThrowsAsync<T>` and inspect the message.
- Mock only external boundaries (HTTP, clock, queue). Prefer fakes for repositories.
- No `Thread.Sleep`/`Task.Delay` waits; await the condition.
- Run: `{{TEST_CMD}}` (for example `dotnet test`).

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
