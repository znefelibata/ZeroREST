# ZeroREST

**ZeroREST** is a stateful RESTful API fuzzy testing tool that combines OpenAPI-driven test generation with differential testing against a local MySQL model.

> **Note:** This project leverages the [RestTestGen](https://github.com/SeUniVr/RestTestGen) framework. It detects discrepancies between API behavior and the expected underlying data model, surfacing bugs, logical errors, and data integrity issues that traditional black-box testing misses.

## Framework
![workflow2](https://gitee.com/xxp121/figurebed/raw/master/img/workflow2.png)


## Bugs Found in Experiments

ZeroREST has been validated against real-world APIs (GitLab and WordPress), uncovering **23 confirmed bugs** (11 in GitLab, 12 in WordPress) spanning eight categories. More detailed descriptions can be found in the reported issue.

### Bug Classification Summary

| Bug Category | GitLab | WordPress | Total |
|--------------|--------|-----------|-------|
| Duplicate ID | 0 | 2 | 2 |
| Duplicate Deletion | 2 | 0 | 2 |
| Post-Deletion Access | 1 | 2 | 3 |
| Empty/Null Value Error | 2 | 2 | 4 |
| URL Encoding Error | 0 | 3 | 3 |
| Unsupported Function | 0 | 3 | 3 |
| Boundary ID Processing | 3 | 0 | 3 |
| Creation Failure | 3 | 0 | 3 |
| **Total** | **11** | **12** | **23** |

---

### Full Bug List

| #  | Category | Server | Endpoint | Method | Issue                                                           |
|----|----------|--------|----------|--------|-----------------------------------------------------------------|
| 1  | Empty/Null Value Error | GitLab | `/groups/{id}/badges/{badge_id}` | PUT | [#585869](https://gitlab.com/gitlab-org/gitlab/-/issues/585869) |
| 2  | Empty/Null Value Error | GitLab | `/admin/ci/variables/{key}` | PUT | [#585849](https://gitlab.com/gitlab-org/gitlab/-/issues/585849) |
| 3  | Creation Failure | GitLab | `/groups` | POST | [#586605](https://gitlab.com/gitlab-org/gitlab/-/issues/586605) |
| 4  | Creation Failure | GitLab | `/admin/ci/variables` | POST | [#585847](https://gitlab.com/gitlab-org/gitlab/-/issues/585847) |
| 5  | Creation Failure | GitLab | `/groups/{id}/badges` | POST | [#585868](https://gitlab.com/gitlab-org/gitlab/-/issues/585868) |
| 6  | Duplicate Deletion | GitLab | `/broadcast_messages/{id}` | DELETE | [#585861](https://gitlab.com/gitlab-org/gitlab/-/issues/585861) |
| 7  | Duplicate Deletion | GitLab | `/projects/{id}/badges/{badge_id}` | DELETE | [#585867](https://gitlab.com/gitlab-org/gitlab/-/issues/585867) |
| 8  | Post-Deletion Access | GitLab | `/admin/ci/variables/{key}` | PUT/DELETE | [#585858](https://gitlab.com/gitlab-org/gitlab/-/issues/585858) |
| 9  | Boundary ID Processing | GitLab | `/admin/clusters/{cluster_id}` | PUT | [#585854](https://gitlab.com/gitlab-org/gitlab/-/issues/585854) |
| 10 | Boundary ID Processing | GitLab | `/projects/{id}/badges/{badge_id}` | PUT | [#585870](https://gitlab.com/gitlab-org/gitlab/-/issues/585870) |
| 11 | Boundary ID Processing | GitLab | `/projects/{id}/jobs/{job_id}/play` | POST | [#585866](https://gitlab.com/gitlab-org/gitlab/-/issues/585866) |
| 12 | Post-Deletion Access | WordPress | `/posts/{id}` | DELETE/PUT | [#64516](https://core.trac.wordpress.org/ticket/64516#ticket) |
| 13 | Post-Deletion Access | WordPress | `/pages/{id}/autosaves` | DELETE/POST | [#64516](https://core.trac.wordpress.org/ticket/64516#ticket) |
| 14 | URL Encoding Error | WordPress | `/tags` | GET | [#64541](https://core.trac.wordpress.org/ticket/64541#ticket) |
| 15 | URL Encoding Error | WordPress | `/tags` | GET | [#64542](https://core.trac.wordpress.org/ticket/64542#ticket) |
| 16 | URL Encoding Error | WordPress | `/tags` | GET | [#64542](https://core.trac.wordpress.org/ticket/64542#ticket) |
| 17 | Duplicate ID | WordPress | `/categories/{id}` | POST | [#64801](https://core.trac.wordpress.org/ticket/64801#ticket) |
| 18 | Duplicate ID | WordPress | `/posts` | POST | [#64801](https://core.trac.wordpress.org/ticket/64801#ticket) |
| 19 | Empty/Null Value Error | WordPress | `/categories` | POST | [#64800](https://core.trac.wordpress.org/ticket/64800#ticket) |
| 20 | Empty/Null Value Error | WordPress | `/tags` | POST | [#64799](https://core.trac.wordpress.org/ticket/64799#ticket) |
| 21 | Unsupported Function | WordPress | `/categories/{id}` | DELETE | reported via email |
| 22 | Unsupported Function | WordPress | `/tags/{id}` | DELETE | reported via email |
| 23 | Unsupported Function | WordPress | `/users/me` | DELETE | reported via email |

---

### Bug Category Descriptions

- **Duplicate ID**: The API incorrectly allows creating resources with identifiers that already exist in the system, leading to data integrity violations. ZeroREST detects this by comparing POST response codes against the shadow database state, where the insert would fail with a uniqueness constraint.

- **Duplicate Deletion**: The API accepts repeated DELETE requests on the same resource without returning an appropriate error (e.g., `404 Not Found`). The shadow database model correctly rejects the second deletion, exposing the discrepancy.

- **Post-Deletion Access**: After a resource is deleted, the API continues to serve or accept modifications to that resource (returning 2XX) instead of `404 Not Found`. The differential oracle flags these responses because the shadow database contains no matching record.

- **Empty/Null Value Error**: In WordPress, endpoints accept empty string values for required fields such as `name`, silently creating malformed records. In GitLab, null-value updates violate data integrity constraints that the underlying model enforces. Both manifest as false-positive 2XX responses.

- **URL Encoding Error**: Endpoints silently accept URL-encoded special characters (e.g., `%25`, `%27`, `%2500`) in parameter values and return 2XX status codes rather than rejecting malformed input. The shadow database model rejects or transforms these values, exposing the inconsistency.

- **Unsupported Function**: Certain API operations trigger internal server errors (5XX), indicating that the functionality is incomplete or contains unhandled edge cases at the implementation level.

- **Boundary ID Processing**: The API fails to properly handle extreme or boundary ID values (e.g., very large integers, negative values, or IDs of non-existent resources), producing inconsistent responses that diverge from the expected shadow database behavior.

- **Creation Failure**: Resource-creation requests (POST) unexpectedly trigger HTTP 5XX errors instead of succeeding or returning a well-formed client error, indicating unhandled server-side logic failures during the creation workflow.

---

## <a id="getting-started"></a> Getting Started

1. Clone the ZeroREST repo
```bash
git clone https://github.com/your-org/ZeroREST.git
cd ZeroREST
```

2. Save the OpenAPI specification (JSON or YAML) of the target service in the `apis/<your-api>/specifications/` folder
```
apis/
  bookstore/
    specifications/
      openapi.json   ← place your spec here
```

3. (Optional) Create `apis/<your-api>/api-config.yml` to configure API name, auth, and reset commands:
```yaml
name: Bookstore
specificationFileName: openapi.json
host: "http://localhost:8080/"
authenticationCommands:
  default: "echo {\"name\": \"Authorization\", \"value\": \"Bearer TOKEN\", \"in\": \"header\", \"duration\": 3600}"
```

4. Edit `rtg-config.yml` in the project root to point to your API and select a testing strategy:
```yaml
apiUnderTest: bookstore
strategyClassName: NominalAndErrorStrategy
```

5. Build and run ZeroREST:
```bash
./gradlew run
```
> On Windows use `gradlew.bat run`. Alternatively, build and run via Docker:
> ```bash
> docker build -t zerorest .
> docker run --rm -v ./:/app --network host zerorest
> ```

Results are written to `apis/<your-api>/results/` after the session completes.

---

### Configuration Reference

#### `api-config.yml` options

| Key | Description | Default |
|-----|-------------|---------|
| `name` | Display name for the API | directory name |
| `specificationFileName` | OpenAPI spec filename in `specifications/` | `openapi.json` |
| `authenticationCommands` | Map of `<label, command>` for auth. See [Authentication](#auth) | — |

#### `rtg-config.yml` options

| Key | Description | Default |
|-----|-------------|---------|
| `apiUnderTest` | API directory name under `apis/` | — |
| `strategyClassName` | Testing strategy (`NominalAndErrorStrategy`, `SqlDiffStrategy`) | `NominalAndErrorStrategy` |
| `logVerbosity` | Log level: `DEBUG`, `INFO`, `WARN`, `ERROR` | `INFO` |
| `testingSessionName` | Label used in report filenames | `test-session-<timestamp>` |
| `resultsLocation` | Where to write results: `local` or `global` | `local` |
| `qualifiableNames` | Parameter names to qualify (e.g. `id` → `bookId`) | `['id', 'name']` |
| `odgFileName` | Output filename for the Operation Dependency Graph | `odg.dot` |

### <a id="auth"></a>Authentication
> Skip this section if your REST API does not require authentication.

ZeroREST executes authentication commands defined in `api-config.yml` and expects their standard output to be a JSON object with four fields: `name`, `value`, `in` (e.g., `header`, `query`), and `duration` (seconds until re-authentication is needed).

Example output from an authentication script:
```json
{
  "name": "Authorization",
  "value": "Bearer [TOKEN]",
  "in": "header",
  "duration": 600
}
```


