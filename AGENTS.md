# SalesNexus CLI — Agent Reference

> Machine-optimized reference for AI agents using `snx` via subprocess.
> For human documentation see README.md.

## Critical Behaviors

- **Auto-JSON**: When stdout is NOT a TTY (subprocess/pipe), output is JSON automatically. No `--json` flag needed.
- **Status messages → stderr**: "Contact 101 created." goes to stderr. stdout is always clean JSON.
- **Exit code 0** = success, **1** = error.
- **Auto-retry**: HTTP 429/502/503/504 retried 3× with exponential backoff. No agent-side retry needed.
- **Destructive commands** (`delete`, `batch-delete`) require `--yes` flag to skip interactive confirmation.
- **Rate limit**: 10,000 requests/hour per account.
- **Pagination max**: pageSize ≤ 100 (tasks ≤ 200). Use `--all` for full export.

## Environments

| Environment | Base URL | Default? |
|---|---|---|
| **Production** | `https://api.salesnex.us` | **Yes** |
| **Beta** | `https://api-beta.salesnex.us` | No |

API keys are environment-specific. A production key will NOT work on beta.

## Authentication

Set before first use. Persists to `~/.salesnexus/config.toml`.

```
# Production (default)
snx auth login --api-key sn_live_XXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY

# Beta
snx auth login --api-key sn_live_XXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY --profile beta --base-url https://api-beta.salesnex.us
```

Or set env var: `SALESNEXUS_API_KEY=sn_live_...`

Verify: `snx ping` → `{"message":"pong","user":"email","accountId":N}`

## Global Flags (all commands)

| Flag | Effect |
|---|---|
| `--json` | Force JSON (redundant in subprocess) |
| `--csv` | CSV output |
| `--profile NAME` / `-p` | Use named profile |
| `--api-key KEY` | Override API key (hidden) |
| `--base-url URL` | Override base URL (hidden) |

---

## Command Reference

### snx ping

```
snx ping
```

Response:
```json
{"message":"pong","user":"john@acme.com","accountId":42}
```

---

### snx auth

#### login
```
snx auth login --api-key KEY [--base-url URL] [--profile NAME]
```
| Param | Required | Default |
|---|---|---|
| `--api-key`, `-k` | yes | — |
| `--base-url`, `-u` | no | `https://api.salesnex.us` |
| `--profile`, `-p` | no | `default` |

#### status
```
snx auth status [--profile NAME]
```

#### switch
```
snx auth switch PROFILE_NAME
```

#### list
```
snx auth list
```

#### logout
```
snx auth logout [--profile NAME]
```

---

### snx contacts

#### list
```
snx contacts list [--page N] [--page-size N] [--search TEXT] [--all]
```
| Param | Default | Notes |
|---|---|---|
| `--page` | 1 | |
| `--page-size` | 20 | max 100 |
| `--search`, `-s` | — | name/email/company |
| `--all`, `-a` | false | auto-paginates all pages |

Response:
```json
{
  "data": [{"id":N,"firstName":"","lastName":"","email":"","phone":"","company":"","title":"","city":"","state":"","customFields":{}}],
  "totalItems": N,
  "page": N,
  "pageSize": N
}
```

#### get
```
snx contacts get ID
```
Response: single contact object (all fields including customFields).

#### create
```
snx contacts create --first-name NAME [OPTIONS]
```
| Param | Short | Required | Type |
|---|---|---|---|
| `--first-name` | `-f` | **yes** | str |
| `--last-name` | `-l` | no | str |
| `--email` | `-e` | no | str |
| `--phone` | | no | str |
| `--company` | `-c` | no | str |
| `--title` | | no | str |
| `--address` | | no | str |
| `--city` | | no | str |
| `--state` | | no | str |
| `--zip` | | no | str |
| `--country` | | no | str |
| `--manager-id` | | no | int |
| `--custom-field` | `-F` | no | str (repeatable, `key=value`) |

Response: created contact object.  
stderr: `Contact {id} created.`

#### update
```
snx contacts update ID [--first-name ...] [--last-name ...] [--email ...] [--phone ...] [--company ...] [--title ...] [--address ...] [--city ...] [--state ...] [--zip ...] [--country ...] [--manager-id ...] [--custom-field key=value ...]
```
Same params as create, all optional. Only changed fields sent.  
stderr: `Contact {id} updated.`

#### delete
```
snx contacts delete ID --yes
```
stderr: `Contact {id} deleted.`

#### batch-update
```
snx contacts batch-update (--ids "1,2,3" | --lookup-id N) --field key=value [--field ...]
```
| Param | Short | Notes |
|---|---|---|
| `--ids` | | comma-separated IDs |
| `--lookup-id` | | saved search ID |
| `--field` | `-F` | repeatable `key=value` |

One of `--ids` or `--lookup-id` required.

Response:
```json
{"successCount":N,"deletedCount":N,"opportunitiesDeletedCount":N,"failedIds":[]}
```

#### batch-delete
```
snx contacts batch-delete (--ids "1,2,3" | --lookup-id N) --yes
```
Response: same shape as batch-update.

---

### snx opps

#### list
```
snx opps list [--page N] [--page-size N] [--goal-id N] [--stage-id N] [--contact-id N] [--all]
```
| Param | Short | Default |
|---|---|---|
| `--page` | | 1 |
| `--page-size` | | 20 |
| `--goal-id` | `-g` | — |
| `--stage-id` | | — |
| `--contact-id` | `-c` | — |
| `--all` | `-a` | false |

Response: `{data:[{id,title,contactId,goalId,currentStageId,amount,currency,createdAt,customFields,opportunityContacts}],totalItems,page,pageSize}`

#### get
```
snx opps get ID
```

#### create
```
snx opps create --contact-id N --goal-id N [OPTIONS]
```
| Param | Short | Required | Type |
|---|---|---|---|
| `--contact-id` | `-c` | **yes** | int |
| `--goal-id` | `-g` | **yes** | int |
| `--stage-id` | | no | int |
| `--owner-id` | | no | int |
| `--title` | `-t` | no | str |
| `--amount` | | no | float |
| `--currency` | | no | str |
| `--custom-field` | `-F` | no | str (repeatable, `key=value`) |

#### update
```
snx opps update ID [--stage-id N] [--owner-id N] [--title TEXT] [--amount N] [--currency CODE] [--custom-field key=value ...]
```

#### delete
```
snx opps delete ID --yes
```

#### batch-update
```
snx opps batch-update --ids "1,2,3" --field key=value [--field ...]
```

#### batch-delete
```
snx opps batch-delete --ids "1,2,3" --yes
```

---

### snx tasks

#### list
```
snx tasks list [--page N] [--page-size N] [--scope own|all] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
```
| Param | Default | Notes |
|---|---|---|
| `--page` | 1 | |
| `--page-size` | 20 | max 200 |
| `--scope` | `own` | `own` or `all` |
| `--start-date` | — | YYYY-MM-DD |
| `--end-date` | — | YYYY-MM-DD |

Response: `{data:[{id,title,details,type,priority,status,dateFrom,dateTo,assignedToUserId,contactId,opportunityId}],totalItems,page,pageSize}`

#### get
```
snx tasks get ID [--scope own|all]
```

#### create
```
snx tasks create --title TEXT [OPTIONS]
```
| Param | Short | Required | Type |
|---|---|---|---|
| `--title` | `-t` | **yes** | str |
| `--details` | `-d` | no | str |
| `--date-from` | | no | ISO datetime |
| `--date-to` | | no | ISO datetime |
| `--type` | | no | str (Call, Email, Meeting, etc.) |
| `--priority` | | no | str (High, Normal, Low) |
| `--color` | | no | str |
| `--assigned-to` | | no | int (user ID) |
| `--contact-id` | `-c` | no | int |
| `--opportunity-id` | `-o` | no | int |
| `--group-id` | `-g` | no | int |

#### update
```
snx tasks update ID [--title TEXT] [--details TEXT] [--date-from DT] [--date-to DT] [--type T] [--priority P] [--color C] [--status S] [--assigned-to UID]
```

#### delete
```
snx tasks delete ID --yes
```

---

### snx notes

#### list
```
snx notes list [--contact-id N] [--opportunity-id N] [--page N] [--page-size N]
```

Response: `[{id,contactId,opportunityId,noteText,createdOn,createdBy}]` (may be flat array).

#### get
```
snx notes get ID
```

#### create
```
snx notes create --text TEXT (--contact-id N | --opportunity-id N)
```
| Param | Short | Required |
|---|---|---|
| `--text` | `-t` | **yes** |
| `--contact-id` | `-c` | one of these required |
| `--opportunity-id` | `-o` | one of these required |

#### update
```
snx notes update ID --text TEXT
```

#### delete
```
snx notes delete ID --yes
```

---

### snx goals

Goals contain pipelines → stages (sales pipeline).

#### list
```
snx goals list [--page N] [--page-size N] [--sort-by FIELD] [--sort-desc]
```

#### get
```
snx goals get ID
```
Response:
```json
{
  "id": N,
  "name": "",
  "description": "",
  "pipelines": [
    {
      "id": N,
      "name": "",
      "isDefault": true,
      "stages": [
        {"id": N, "name": "", "order": N, "slaHours": N, "isConversion": false}
      ]
    }
  ]
}
```

#### create
```
snx goals create --name TEXT [--description TEXT]
```
| Param | Short | Required |
|---|---|---|
| `--name` | `-n` | **yes** |
| `--description` | `-d` | no |

#### update
```
snx goals update ID [--name TEXT] [--description TEXT]
```

#### delete
```
snx goals delete ID --yes
```

---

### snx fields

Custom field definitions for contacts and opportunities.

#### list
```
snx fields list [--entity contact|opportunity]
```
Default entity: `contact`.

Response: `[{id,name,label,type,isSystem,isRequired,isDropDown,multiSelect,defaultValue,options}]`

**Type codes**: 0=character, 1=currency, 2=date, 3=numeric, 4=phone, 5=time, 6=checkbox, 7=percentage, 8=image

#### create
```
snx fields create --name TEXT [OPTIONS]
```
| Param | Short | Default | Type |
|---|---|---|---|
| `--entity` | `-e` | `contact` | `contact` or `opportunity` |
| `--name` | `-n` | — (required) | str |
| `--label` | `-l` | — | str |
| `--type` | `-t` | `character` | see type codes |
| `--required` | | false | flag |
| `--dropdown` | | false | flag |
| `--multi-select` | | false | flag |
| `--default` | | — | str |
| `--options` | | — | comma-separated str |

---

### snx templates

Email templates / campaigns.

#### list
```
snx templates list [--sort-by FIELD] [--sort-desc] [--mode bulk|triggered]
```

#### get
```
snx templates get ID
```
Response: `{id,name,objective,status,mode,scheduleAt,segmentId,createdAt,updatedAt}`

#### stats
```
snx templates stats ID
```
Response: `{sent,opens,clicks,bounces,unsubscribes,complaints}`

#### create
```
snx templates create --name TEXT [--objective TEXT] [--mode bulk|triggered] [--segment-id N]
```
| Param | Short | Required | Default |
|---|---|---|---|
| `--name` | `-n` | **yes** | — |
| `--objective` | | no | — |
| `--mode` | | no | `bulk` |
| `--segment-id` | | no | — |

#### update
```
snx templates update ID [--name TEXT] [--objective TEXT] [--status TEXT]
```

#### delete
```
snx templates delete ID --yes
```

---

### snx reports

#### list
```
snx reports list
```

#### get
```
snx reports get ID
```
Response: `{id,title,specJson,narrativeJson,isPublic,createdAt,lastRunAt}`

#### create
```
snx reports create --title TEXT [--spec JSON] [--public]
```

#### update
```
snx reports update ID [--title TEXT] [--spec JSON] [--public|--private]
```

#### delete
```
snx reports delete ID --yes
```

---

### snx lookups

Saved searches (lookups) with filter conditions (segments) and column configs (layouts).

#### lookups list/get/create
```
snx lookups list
snx lookups get ID
snx lookups create --name TEXT [--segment-id N] [--layout-id N]
```

#### lookups segments list/get/create/update
```
snx lookups segments list
snx lookups segments get ID
snx lookups segments create --name TEXT [--spec JSON]
snx lookups segments update ID [--name TEXT] [--spec JSON]
```
`--spec`: JSON string with segment conditions.

#### lookups layouts list/get/create/update
```
snx lookups layouts list
snx lookups layouts get ID
snx lookups layouts create --name TEXT [--spec JSON]
snx lookups layouts update ID [--name TEXT] [--spec JSON]
```

---

### snx docs

Documents attached to contacts/groups/opportunities.

#### list
```
snx docs list [--page N] [--page-size N] [--contact-id N] [--group-id N] [--opportunity-id N] [--scope own|all] [--all]
```

#### get
```
snx docs get ID [--scope own|all]
```
Response: `{id,userId,contactId,groupId,opportunityId,description,originalFileName,mime,size,tags,sourceUrl,sourceType,createdAt}`

#### create
```
snx docs create --url URL [--description TEXT] [--contact-id N] [--group-id N] [--opportunity-id N] [--tags TEXT]
```
| Param | Short | Required |
|---|---|---|
| `--url` | | **yes** |
| `--description` | `-d` | no |
| `--contact-id` | `-c` | no |
| `--group-id` | `-g` | no |
| `--opportunity-id` | `-o` | no |
| `--tags` | | no (comma-separated) |

#### delete
```
snx docs delete ID [--scope own|all] --yes
```

---

### snx forms

Web forms for lead capture.

#### list
```
snx forms list
```
Response: `[{id,name,slug,status,isWiretap,createdAt}]`

#### get
```
snx forms get ID
```

#### create
```
snx forms create --name TEXT [--slug TEXT] [--redirect-url URL] [--settings JSON]
```

#### update
```
snx forms update ID [--name TEXT] [--slug TEXT] [--redirect-url URL] [--settings JSON]
```

#### delete
```
snx forms delete ID --yes
```

#### embed
```
snx forms embed ID
```
Returns HTML embed code snippet.

#### unpublish
```
snx forms unpublish ID
```

---

### snx users

Read-only. Lists account team members.

#### list
```
snx users list
```
Response: `[{id,username,email,isActive,securityLevel}]`

#### get
```
snx users get ID
```

---

## Common Workflows

### Discovery (run first time)
```bash
snx ping
snx users list
snx goals list
snx fields list
snx fields list --entity opportunity
```

### Create contact with note and opportunity
```bash
# Step 1: Create contact — capture ID from stdout JSON
snx contacts create --first-name "Jane" --last-name "Doe" --email "jane@acme.com" --company "Acme Corp"
# → {"id": 101, ...}

# Step 2: Add note
snx notes create --contact-id 101 --text "Initial outreach via email"

# Step 3: Create opportunity (need goal-id from `snx goals list`)
snx opps create --contact-id 101 --goal-id 5 --title "Acme Enterprise" --amount 50000
```

### Search → Inspect → Update
```bash
snx contacts list --search "Acme Corp"
snx contacts get 101
snx contacts update 101 --custom-field "status=Qualified" --custom-field "score=85"
```

### Bulk update via lookup
```bash
snx lookups list
snx contacts batch-update --lookup-id 7 --field "status=Inactive" --yes
```

### Export all contacts
```bash
snx contacts list --all
```
Returns complete JSON array of all contacts (auto-paginates with pageSize=100).

### Get pipeline structure
```bash
snx goals get 5
```
Returns goal → pipelines → stages hierarchy.

### Move opportunity stage
```bash
snx opps update 200 --stage-id 13
```

### Campaign stats
```bash
snx templates list
snx templates stats 42
```

## Error Response Patterns

Errors print to **stderr** only. stdout stays empty on error.

| HTTP Status | stderr Message |
|---|---|
| 401 | `Invalid or expired API key. Run 'snx auth login' to configure.` |
| 403 | `Permission denied.` |
| 404 | `Resource not found.` |
| 409 | `Conflict: {details}` |
| 422 | `Validation error: {details}` |
| 429 | Auto-retried. If persistent: `Rate limit exceeded.` |
| 500 | `Server error. Try again later.` |

## Custom Fields — Key Rules

1. Set via `--custom-field key=value` (or `-F key=value`). Repeatable.
2. If field name doesn't exist, API **auto-creates** it as Character type.
3. To create fields with specific types first: `snx fields create --name score --type numeric`
4. Custom fields appear in `customFields` object of contact/opportunity responses.
5. In batch-update, use `--field key=value` (not `--custom-field`).

## Environment Variables

| Variable | Effect |
|---|---|
| `SALESNEXUS_API_KEY` | Override API key |
| `SALESNEXUS_BASE_URL` | Override base URL (default: `https://api.salesnex.us`, beta: `https://api-beta.salesnex.us`) |
| `SALESNEXUS_PROFILE` | Override profile name |
| `NO_COLOR` | Disable colors |
