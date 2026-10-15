# Bringing Jira work into Compass

There are three ways, in order of how much access they need:

| Option | Needs | How |
|---|---|---|
| Paste | Nothing | Paste the story or defect into the Goal box |
| CSV export | Nothing | In Jira, use *Export > CSV (current fields)*. In Compass, open *Quick prompt > Import Jira CSV*, or paste the story into the Workflow coach |
| Automatic fetch | Read-only API access that your organization allows, plus a personal token | Setup > 4: choose Jira Cloud or Data Center, enter the https base URL, and tick "my organization allows read-only API access". Put the token in an environment variable, `COMPASS_JIRA_TOKEN` by default |

## Automatic fetch details

- **Data Center / Server:** uses a personal access token sent as `Authorization: Bearer`.
- **Jira Cloud:** uses your account email plus an API token (basic auth).
- **Fetch one issue:** `GET {base}/rest/api/2/issue/{KEY}?fields=summary,description,issuetype,priority,status,labels,components[,<acceptance field>]`
- **My open issues:**
  - Data Center: `GET /rest/api/2/search`
  - Cloud: `GET /rest/api/3/search/jql`
  - Default JQL: `assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC`
- **Safety:**
  - Only GET requests, only to the one https host you configured.
  - Timeout 20 s.
  - The token is never written to disk or logs, and the fetched text is shown to you, not stored.
- **Acceptance-criteria field:** many Jira sites keep acceptance criteria in a custom field. Put its id, for example `customfield_12345`, in Setup.

## Start straight into a Jira issue

```
Start-Coach.bat C:\code\my-repo ABC-123
python -m compass --project C:\code\my-repo --jira ABC-123
```

Compass opens the Workflow coach with that project selected and fetches the issue. If you launch it with a project folder, that folder is added to your allowed folders.

## Corporate networks

If your Jira sits behind a TLS-inspecting proxy, point Python at your company CA bundle with `SSL_CERT_FILE`. Standard `HTTPS_PROXY` settings are respected. If the API is not approved, use paste or CSV; everything else works the same.
