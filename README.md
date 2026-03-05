# ZeroREST
***

**ZeroREST** is a stateful RESTful API fuzzy testing tool that combines OpenAPI-driven test generation with differential testing against a local MySQL model.

> **Note:** This project leverages the [RestTestGen](https://github.com/SeUniVr/RestTestGen) framework. It detects discrepancies between API behavior and the expected underlying data model, surfacing bugs, logical errors, and data integrity issues that traditional black-box testing misses.

---
## Framework
![framework—en](https://gitee.com/xxp121/figurebed/raw/master/img/workflow2.png)

---

## Bugs Found in Experiments

ZeroREST has been validated against real-world APIs. The table below lists confirmed bugs discovered during testing:

| # | Classification | Server | Endpoint | Method | Issue |
|---|----------------|--------|----------|--------|-------|
| 1 | Logical: use after delete | GitLab | `/users/{id}/custom_attributes` `/users/{id}/custom_attributes/{key}` | GET / GET/PUT/DELETE | [#335276](https://gitlab.com/gitlab-org/gitlab/-/issues/335276) |
| 2 | Logical: use after delete | GitLab | `/projects/{id}/custom_attributes` `/projects/{id}/custom_attributes/{key}` | GET / GET/PUT/DELETE | [#335276](https://gitlab.com/gitlab-org/gitlab/-/issues/335276) |
| 3 | Logical: use after delete | GitLab | `/groups/{id}/custom_attributes` `/groups/{id}/custom_attributes/{key}` | GET / GET/PUT/DELETE | [#335276](https://gitlab.com/gitlab-org/gitlab/-/issues/335276) |
| 4 | Logical: double delete | GitLab | `/projects/{id}/services/github` | DELETE | [#360147](https://gitlab.com/gitlab-org/gitlab/-/issues/360147) |
| 5 | Invalid parameter: UTF-8 | GitLab | `/hooks` | POST | [#334606](https://gitlab.com/gitlab-org/gitlab/-/issues/334606) |
| 6 | Invalid parameter: UTF-8 | GitLab | `/projects/{id}/metrics/user_starred_dashboards` | POST | [#334606](https://gitlab.com/gitlab-org/gitlab/-/issues/334606) |
| 7 | Invalid parameter: UTF-8 | GitLab | `/admin/cluster/add` | POST | [#346121](https://gitlab.com/gitlab-org/gitlab/-/issues/346121) |
| 8 | Invalid parameter: UTF-8 | GitLab | `/projects/{id}/cluster/user` | POST | [#346121](https://gitlab.com/gitlab-org/gitlab/-/issues/346121) |
| 9 | Invalid parameter: UTF-8 | GitLab | `/groups/{id}/cluster/user` | POST | [#346121](https://gitlab.com/gitlab-org/gitlab/-/issues/346121) |
| 10 | Invalid parameter: UTF-8 | GitLab | `/projects/{id}/export` | POST | [#346121](https://gitlab.com/gitlab-org/gitlab/-/issues/346121) |
| 11 | Invalid parameter: special characters | GitLab | `/projects/{project_id}/variables/{key}` | POST | [#360662](https://gitlab.com/gitlab-org/gitlab/-/issues/360662) |
| 12 | Invalid parameter: enum type with bad value | GitLab | `/projects/{id}/environments` | GET | [#360138](https://gitlab.com/gitlab-org/gitlab/-/issues/360138) |
| 13 | Invalid parameter: long string with special characters | GitLab | `/projects/{id}/repository/commits` | GET | [#356922](https://gitlab.com/gitlab-org/gitlab/-/issues/356922) |
| 14 | Invalid parameter: special characters | GitLab | `/projects/{id}/repository/commits` | POST | [#360312](https://gitlab.com/gitlab-org/gitlab/-/issues/360312) |
| 15 | Logical: false logic | GitLab | `/projects/{id}/repository/branches` | POST | [#360313](https://gitlab.com/gitlab-org/gitlab/-/issues/360313) |
| 16 | Logical: reference loop | GitLab | `/projects/{id}/fork/{forked_from_id}` | POST | [#346563](https://gitlab.com/gitlab-org/gitlab/-/issues/346563) |
| 17 | Unsupported function | GitLab | `/projects` | POST | [#356921](https://gitlab.com/gitlab-org/gitlab/-/issues/356921) |
| 18 | Unsupported function | WordPress | `/categories/{id}` | DELETE | reported via email |
| 19 | Unsupported function | WordPress | `/tags/{id}` | DELETE | reported via email |
| 20 | Logical: duplicated id | WordPress | `/users` | POST | reported via email |

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


