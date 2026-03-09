# SalesNexus CLI (`snx`)

A command-line interface for the [SalesNexus](https://salesnexus.com) CRM.
Designed for humans **and** AI agents — output auto-switches to JSON when piped.

> **Version:** 0.1.1 &nbsp;|&nbsp; **API:** SalesNexus Public API v1 &nbsp;|&nbsp; **Python:** ≥ 3.10

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Environments](#environments)
- [Authentication & Configuration](#authentication--configuration)
- [Global Options](#global-options)
- [Output Formats](#output-formats)
- [Command Reference](#command-reference)
  - [ping](#ping)
  - [auth](#auth)
  - [contacts](#contacts)
  - [transcripts](#transcripts)
  - [opps (opportunities)](#opps-opportunities)
  - [tasks](#tasks)
  - [notes](#notes)
  - [goals](#goals)
  - [fields](#fields)
  - [templates](#templates)
  - [reports](#reports)
  - [lookups](#lookups)
  - [docs (documents)](#docs-documents)
  - [forms](#forms)
  - [users](#users)
- [Pagination](#pagination)
- [Custom Fields](#custom-fields)
- [Batch Operations](#batch-operations)
- [AI Agent Integration Guide](#ai-agent-integration-guide)
- [Error Handling & Exit Codes](#error-handling--exit-codes)
- [Rate Limits](#rate-limits)
- [Environment Variables](#environment-variables)
- [Shell Completions](#shell-completions)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Installation

### From source (recommended for now)

```bash
cd salesnexus-cli
pip install -e .
```

### With dev dependencies (for testing)

```bash
pip install -e ".[dev]"
```

### Verify installation

```bash
snx --version
# snx 0.1.1
```

> **Note:** If `snx` is not on your PATH after install, add the Python Scripts directory:
> - **Windows:** `%LOCALAPPDATA%\...\Python3XX\Scripts`
> - **macOS/Linux:** `~/.local/bin`

---

## Quick Start

```bash
# 1. Save your API key
snx auth login --api-key sn_live_AbCdEfGh.01234567890123456789012345678901

# 2. Verify connection
snx ping
# ✓ Connected as john@acme.com (account 42)

# 3. List your contacts
snx contacts list

# 3b. List recent call transcripts
snx transcripts list --page-size 5

# 4. Create a contact
snx contacts create --first-name "Jane" --last-name "Doe" --email "jane@acme.com" --company "Acme Corp"

# 5. Get JSON output (for scripting or AI agents)
snx contacts list --json
```

---

## Environments

SalesNexus provides two public API environments:

| Environment | Base URL | Description |
|-------------|----------|-------------|
| **Production** | `https://api.salesnex.us` | Live data. This is the **default**. |
| **Beta** | `https://api-beta.salesnex.us` | Pre-release features. Data may be reset. |

The CLI defaults to **production**. To use beta, pass `--base-url` when logging in:

```bash
# Production (default — no --base-url needed)
snx auth login --api-key sn_live_...

# Beta
snx auth login --api-key sn_live_... --profile beta --base-url https://api-beta.salesnex.us
```

You can maintain profiles for both environments simultaneously:

```bash
snx auth switch default    # → production
snx auth switch beta       # → beta
```

> **Important:** API keys are environment-specific. A production key will not work on beta, and vice versa.

---

## Authentication & Configuration

### API Key

You need a SalesNexus API key to use the CLI. API keys have the format:

```
sn_live_XXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
         ├─────┘ └──────────────────────────────┘
         prefix          secret (32 chars)
```

Generate API keys from the SalesNexus web app under **Settings → API Keys**, or ask your account administrator.

### Profiles

The CLI supports named profiles (like AWS CLI), stored in `~/.salesnexus/config.toml`:

```toml
active_profile = "default"

[profiles.default]
api_key = "sn_live_AbCdEfGh.01234567890123456789012345678901"
base_url = "https://api.salesnex.us"

[profiles.beta]
api_key = "sn_live_XyZwVuTs.98765432109876543210987654321098"
base_url = "https://api-beta.salesnex.us"
```

### Credential Precedence

The CLI resolves credentials in this order (highest priority first):

| Priority | Source | Example |
|----------|--------|---------|
| 1 (highest) | CLI flags | `--api-key sn_live_...` |
| 2 | Environment variables | `SALESNEXUS_API_KEY=sn_live_...` |
| 3 (lowest) | Config file profile | `~/.salesnexus/config.toml` |

The profile is selected by: `--profile` flag → `SALESNEXUS_PROFILE` env var → `active_profile` in config.

### Managing Profiles

```bash
# Save a profile
snx auth login --api-key sn_live_AbCdEfGh.01234567890123456789012345678901

# Save a profile for the beta environment
snx auth login --api-key sn_live_XyZw... --profile beta --base-url https://api-beta.salesnex.us

# List all profiles
snx auth list

# Switch active profile
snx auth switch staging

# Check current status
snx auth status

# Remove a profile
snx auth logout --profile staging
```

---

## Global Options

These flags are available on **every** command:

| Flag | Short | Description |
|------|-------|-------------|
| `--json` | | Force JSON output. Auto-enabled when stdout is not a TTY (piped). |
| `--csv` | | Force CSV output. |
| `--profile NAME` | `-p` | Use a specific config profile for this command. |
| `--api-key KEY` | | Override API key for this command (hidden from help). |
| `--base-url URL` | | Override base URL for this command (hidden from help). |
| `--version` | `-v` | Print version and exit. |
| `--install-completion` | | Install shell completion for your current shell. |
| `--help` | | Show help for any command. |

### Examples

```bash
# Use a different profile for one command
snx --profile staging contacts list

# Force JSON output
snx --json contacts get 123

# CSV output piped to a file
snx --csv contacts list --all > contacts.csv

# One-off API key (e.g. in CI)
snx --api-key sn_live_... ping
```

---

## Transcripts

Read call transcripts created automatically by integrated calling providers.

### List transcripts

```bash
snx transcripts list
snx transcripts list --contact-id 123
snx transcripts list --provider RingCentral --status completed
snx transcripts list --search "pricing objection" --all --json
```

Supported filters:

- `--page`
- `--page-size`
- `--contact-id`
- `--user-id`
- `--provider`
- `--status`
- `--from`
- `--to`
- `--search`
- `--all`

### Get one transcript

```bash
snx transcripts get 987
snx --json transcripts get 987
```

List output includes summary columns such as transcript ID, contact ID, provider, status, duration, and creation date. `get` returns the full transcript payload including `transcriptText` and `recordingUrl` when available.

---

## Output Formats

The CLI supports three output formats:

### Table (default in interactive terminals)

When you run `snx` in a terminal, you get rich formatted tables:

```
┏━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ id  ┃ firstName ┃ lastName ┃ email              ┃ company       ┃
┡━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 101 │ Jane      │ Doe      │ jane@acme.com      │ Acme Corp     │
│ 102 │ John      │ Smith    │ john@widgets.io    │ Widgets Inc   │
└─────┴───────────┴──────────┴────────────────────┴───────────────┘
          Page 1 — 2 of 48 total
```

For single records (`get` commands), a key-value table is shown:

```
┃ id        ┃ 101               ┃
┃ firstName ┃ Jane              ┃
┃ lastName  ┃ Doe               ┃
┃ email     ┃ jane@acme.com     ┃
┃ company   ┃ Acme Corp         ┃
┃ ...       ┃                   ┃
```

### JSON (default when piped / for AI agents)

When stdout is not a TTY (e.g., piped to another program or called by an AI agent via subprocess), the CLI **automatically** outputs JSON. You can also force it with `--json`.

**List commands** return:

```json
{
  "data": [
    {
      "id": 101,
      "firstName": "Jane",
      "lastName": "Doe",
      "email": "jane@acme.com",
      "company": "Acme Corp",
      ...
    }
  ],
  "totalItems": 48,
  "page": 1,
  "pageSize": 20
}
```

**Get commands** return the raw object:

```json
{
  "id": 101,
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane@acme.com",
  "phone": "555-0101",
  "company": "Acme Corp",
  "title": "VP Sales",
  "address": "123 Main St",
  "city": "Houston",
  "state": "TX",
  "zip": "77001",
  "country": "US",
  "managerUserId": 5,
  "createdAt": "2025-06-15T10:30:00Z",
  "updatedAt": "2026-02-20T14:22:00Z",
  "customFields": {
    "lead_source": "Trade Show",
    "industry": "Manufacturing"
  }
}
```

### CSV

Use `--csv` for spreadsheet-compatible output:

```csv
id,firstName,lastName,email,company
101,Jane,Doe,jane@acme.com,Acme Corp
102,John,Smith,john@widgets.io,Widgets Inc
```

---

## Command Reference

### ping

Verify API connectivity and show the current authenticated user.

```bash
snx ping
# ✓ Connected as john@acme.com (account 42)

snx --json ping
# {"message": "pong", "user": "john@acme.com", "accountId": 42}
```

---

### auth

Manage API key profiles.

#### `snx auth login`

Save an API key to a named profile.

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--api-key` | `-k` | Yes | | API key (`sn_live_...`). |
| `--base-url` | `-u` | No | `https://api.salesnex.us` | API base URL. See [Environments](#environments). |
| `--profile` | `-p` | No | `default` | Profile name to save. |

```bash
snx auth login --api-key sn_live_AbCdEfGh.01234567890123456789012345678901
# Profile 'default' saved.  Base URL: https://api.salesnex.us

snx auth login -k sn_live_XyZw... -p beta -u https://api-beta.salesnex.us
# Profile 'beta' saved.  Base URL: https://api-beta.salesnex.us
```

#### `snx auth status`

Show the active profile and verify connectivity.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--profile` | `-p` | Active profile | Profile to check. |

```bash
snx auth status
# Profile:  default
# Base URL: https://api.salesnex.us
# API Key:  sn_live_AbCd...8901
# ✓ Connected as john@acme.com (account 42)
```

#### `snx auth switch PROFILE`

Set a different profile as active.

```bash
snx auth switch beta
# Active profile set to 'beta'.
```

#### `snx auth list`

List all saved profiles.

```bash
snx auth list
# ┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
# ┃ Name    ┃ Base URL                        ┃ API Key             ┃ Active ┃
# ┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
# │ default │ https://api.salesnex.us         │ sn_live_AbCd...8901 │ ✓      │
# │ beta    │ https://api-beta.salesnex.us    │ sn_live_XyZw...1098 │        │
# └─────────┴────────────────────────────────┴─────────────────────┴────────┘
```

#### `snx auth logout`

Remove a saved profile.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--profile` | `-p` | `default` | Profile to remove. |

```bash
snx auth logout --profile beta
# Profile 'beta' removed.
```

---

### contacts

Full CRUD for contacts, including search, custom fields, and batch operations.

#### `snx contacts list`

List contacts with optional search and pagination.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | | `1` | Page number. |
| `--page-size` | | `20` | Results per page (max 100). |
| `--search` | `-s` | | Search by name, email, company, etc. |
| `--all` | `-a` | `false` | Fetch all pages automatically. |

```bash
# Basic list
snx contacts list

# Search for contacts
snx contacts list --search "Acme"

# Get page 3 with 50 results
snx contacts list --page 3 --page-size 50

# Fetch ALL contacts (auto-paginates)
snx contacts list --all --json
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 101,
      "firstName": "Jane",
      "lastName": "Doe",
      "email": "jane@acme.com",
      "phone": "555-0101",
      "company": "Acme Corp",
      "title": "VP Sales",
      "city": "Houston",
      "state": "TX",
      "customFields": {}
    }
  ],
  "totalItems": 1,
  "page": 1,
  "pageSize": 20
}
```

#### `snx contacts get ID`

Get a single contact with all fields.

```bash
snx contacts get 101

# JSON
snx --json contacts get 101
```

**JSON output:**

```json
{
  "id": 101,
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane@acme.com",
  "phone": "555-0101",
  "company": "Acme Corp",
  "title": "VP Sales",
  "address": "123 Main St",
  "city": "Houston",
  "state": "TX",
  "zip": "77001",
  "country": "US",
  "managerUserId": 5,
  "createdAt": "2025-06-15T10:30:00Z",
  "updatedAt": "2026-02-20T14:22:00Z",
  "customFields": {
    "lead_source": "Trade Show",
    "industry": "Manufacturing"
  }
}
```

#### `snx contacts create`

Create a new contact.

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--first-name` | `-f` | **Yes** | First name. |
| `--last-name` | `-l` | No | Last name. |
| `--email` | `-e` | No | Email address. |
| `--phone` | | No | Phone number. |
| `--company` | `-c` | No | Company name. |
| `--title` | | No | Job title. |
| `--address` | | No | Street address. |
| `--city` | | No | City. |
| `--state` | | No | State. |
| `--zip` | | No | ZIP / postal code. |
| `--country` | | No | Country. |
| `--manager-id` | | No | Assigned manager user ID. |
| `--custom-field` | `-F` | No | Custom field as `key=value` (repeatable). |

```bash
# Minimal
snx contacts create --first-name "Jane"

# Full
snx contacts create \
  --first-name "Jane" \
  --last-name "Doe" \
  --email "jane@acme.com" \
  --phone "555-0101" \
  --company "Acme Corp" \
  --title "VP Sales" \
  --city "Houston" \
  --state "TX" \
  --zip "77001" \
  --custom-field "lead_source=Trade Show" \
  --custom-field "industry=Manufacturing"
```

> **Custom fields** that don't exist yet are **auto-created** by the API as Character type.

#### `snx contacts update ID`

Update an existing contact. Only pass the fields you want to change.

```bash
snx contacts update 101 --email "new@acme.com" --title "Director of Sales"

# Update custom fields
snx contacts update 101 --custom-field "lead_source=Referral"
```

#### `snx contacts delete ID`

Delete a contact (soft delete). Prompts for confirmation unless `--yes` is passed.

```bash
snx contacts delete 101
# Delete contact 101? [y/N]: y
# Contact 101 deleted.

# Skip confirmation
snx contacts delete 101 --yes
```

#### `snx contacts batch-update`

Bulk update contacts by IDs or lookup.

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--ids` | | One of `--ids` or `--lookup-id` | Comma-separated contact IDs. |
| `--lookup-id` | | One of `--ids` or `--lookup-id` | Lookup ID for selection. |
| `--field` | `-F` | **Yes** | Field update as `key=value` (repeatable). |

```bash
# Update by IDs
snx contacts batch-update --ids "101,102,103" --field "status=Active" --field "source=Web"

# Update by lookup (saved search)
snx contacts batch-update --lookup-id 7 --field "status=Inactive"
```

**JSON output:**

```json
{
  "successCount": 3,
  "deletedCount": 0,
  "opportunitiesDeletedCount": 0,
  "failedIds": []
}
```

#### `snx contacts batch-delete`

Bulk delete contacts. Prompts for confirmation unless `--yes`.

```bash
snx contacts batch-delete --ids "101,102,103" --yes

snx contacts batch-delete --lookup-id 7 --yes
```

---

### opps (opportunities)

Manage sales opportunities (deals).

#### `snx opps list`

List opportunities with optional filters.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | | `1` | Page number. |
| `--page-size` | | `20` | Results per page (max 100). |
| `--goal-id` | `-g` | | Filter by goal. |
| `--stage-id` | | | Filter by pipeline stage. |
| `--contact-id` | `-c` | | Filter by contact. |
| `--all` | `-a` | `false` | Fetch all pages. |

```bash
snx opps list
snx opps list --goal-id 5
snx opps list --contact-id 101 --json
snx opps list --all
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 200,
      "title": "Acme Enterprise Deal",
      "contactId": 101,
      "goalId": 5,
      "currentStageId": 12,
      "ownerUserId": 3,
      "amount": 50000.00,
      "currency": "USD",
      "createdAt": "2026-01-10T08:00:00Z",
      "updatedAt": "2026-02-25T16:30:00Z",
      "customFields": {},
      "opportunityContacts": [
        { "contactId": 101, "role": "Decision Maker" }
      ]
    }
  ],
  "totalItems": 1,
  "page": 1,
  "pageSize": 20
}
```

#### `snx opps get ID`

```bash
snx opps get 200
```

#### `snx opps create`

Create a new opportunity.

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--contact-id` | `-c` | **Yes** | Primary contact ID. |
| `--goal-id` | `-g` | **Yes** | Goal (pipeline group) ID. |
| `--stage-id` | | No | Initial stage ID. |
| `--owner-id` | | No | Owner user ID. |
| `--title` | `-t` | No | Opportunity title. |
| `--amount` | | No | Deal amount (decimal). |
| `--currency` | | No | Currency code (e.g., `USD`). |
| `--custom-field` | `-F` | No | Custom field `key=value` (repeatable). |

```bash
snx opps create \
  --contact-id 101 \
  --goal-id 5 \
  --title "Acme Enterprise Deal" \
  --amount 50000 \
  --currency USD \
  --custom-field "priority=High"
```

#### `snx opps update ID`

```bash
snx opps update 200 --stage-id 13 --amount 75000
```

#### `snx opps delete ID`

```bash
snx opps delete 200 --yes
```

#### `snx opps batch-update`

```bash
snx opps batch-update --ids "200,201" --field "priority=Low"
```

#### `snx opps batch-delete`

```bash
snx opps batch-delete --ids "200,201" --yes
```

---

### tasks

Manage tasks assigned to users, linked to contacts/opportunities.

#### `snx tasks list`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | | `1` | Page number. |
| `--page-size` | | `20` | Results per page (max 200). |
| `--scope` | | `own` | `own` (your tasks) or `all`. |
| `--start-date` | | | Filter from date (YYYY-MM-DD). |
| `--end-date` | | | Filter to date (YYYY-MM-DD). |

```bash
snx tasks list
snx tasks list --scope all --start-date 2026-02-01 --end-date 2026-02-28
```

**JSON output** (uses `ApiResponse` envelope):

```json
{
  "data": [
    {
      "id": 500,
      "title": "Follow up call",
      "details": "Discuss proposal",
      "type": "Call",
      "priority": "High",
      "status": "Pending",
      "dateFrom": "2026-02-26T10:00:00Z",
      "dateTo": "2026-02-26T10:30:00Z",
      "assignedToUserId": 3,
      "contactId": 101,
      "opportunityId": null,
      "completedAt": null
    }
  ],
  "totalItems": 1,
  "page": 1,
  "pageSize": 20
}
```

#### `snx tasks get ID`

```bash
snx tasks get 500
snx tasks get 500 --scope all  # if task belongs to another user
```

#### `snx tasks create`

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--title` | `-t` | **Yes** | | Task title. |
| `--details` | `-d` | No | | Description. |
| `--date-from` | | No | | Start date (ISO 8601). |
| `--date-to` | | No | | End date. |
| `--type` | | No | | Task type (e.g. Call, Email, Meeting). |
| `--priority` | | No | | Priority (e.g. High, Normal, Low). |
| `--color` | | No | | Color. |
| `--assigned-to` | | No | Current user | Assigned user ID. |
| `--contact-id` | `-c` | No | | Linked contact. |
| `--opportunity-id` | `-o` | No | | Linked opportunity. |
| `--group-id` | `-g` | No | | Linked group. |

```bash
snx tasks create \
  --title "Follow up call" \
  --details "Discuss proposal" \
  --type "Call" \
  --priority "High" \
  --date-from "2026-02-27T10:00:00" \
  --date-to "2026-02-27T10:30:00" \
  --contact-id 101
```

#### `snx tasks update ID`

```bash
snx tasks update 500 --status "Completed"
snx tasks update 500 --title "Updated title" --priority "Low"
```

#### `snx tasks delete ID`

```bash
snx tasks delete 500 --yes
```

---

### notes

Manage notes attached to contacts or opportunities.

#### `snx notes list`

| Option | Short | Description |
|--------|-------|-------------|
| `--contact-id` | `-c` | Filter by contact. |
| `--opportunity-id` | `-o` | Filter by opportunity. |
| `--page` | | Page number (default: 1). |
| `--page-size` | | Results per page (default: 20). |

```bash
snx notes list --contact-id 101
snx notes list --opportunity-id 200
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 800,
      "contactId": 101,
      "opportunityId": null,
      "noteText": "Called, interested in demo",
      "createdOn": "2026-02-25T14:00:00Z",
      "createdBy": 3
    }
  ]
}
```

#### `snx notes get ID`

```bash
snx notes get 800
```

#### `snx notes create`

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--text` | `-t` | **Yes** | Note text. |
| `--contact-id` | `-c` | One of these | Contact ID. |
| `--opportunity-id` | `-o` | required | Opportunity ID. |

```bash
snx notes create --contact-id 101 --text "Called, interested in enterprise plan"
snx notes create --opportunity-id 200 --text "Sent revised proposal"
```

#### `snx notes update ID`

```bash
snx notes update 800 --text "Updated: Called, requesting demo next week"
```

#### `snx notes delete ID`

```bash
snx notes delete 800 --yes
```

---

### goals

Manage goals (pipeline groups with stages). Goals contain pipelines, which contain stages.

#### `snx goals list`

| Option | Default | Description |
|--------|---------|-------------|
| `--page` | `1` | Page number. |
| `--page-size` | `50` | Results per page. |
| `--sort-by` | | Sort field. |
| `--sort-desc` | `false` | Sort descending. |

```bash
snx goals list
```

#### `snx goals get ID`

Returns the goal with all its pipelines and stages:

```bash
snx --json goals get 5
```

```json
{
  "id": 5,
  "name": "Enterprise Sales",
  "description": "High-value B2B deals",
  "createdBy": 1,
  "createdAt": "2025-03-01T00:00:00Z",
  "updatedAt": "2026-01-15T12:00:00Z",
  "pipelines": [
    {
      "id": 10,
      "goalId": 5,
      "name": "Default Pipeline",
      "description": "",
      "isDefault": true,
      "stages": [
        { "id": 11, "pipelineId": 10, "name": "Prospecting", "order": 1, "slaHours": 72, "isConversion": false },
        { "id": 12, "pipelineId": 10, "name": "Qualification", "order": 2, "slaHours": 48, "isConversion": false },
        { "id": 13, "pipelineId": 10, "name": "Proposal", "order": 3, "slaHours": 168, "isConversion": false },
        { "id": 14, "pipelineId": 10, "name": "Closed Won", "order": 4, "slaHours": null, "isConversion": true }
      ]
    }
  ]
}
```

#### `snx goals create`

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--name` | `-n` | **Yes** | Goal name. |
| `--description` | `-d` | No | Goal description. |

```bash
snx goals create --name "SMB Sales" --description "Small and mid-market deals"
```

#### `snx goals update ID`

```bash
snx goals update 5 --name "Enterprise Sales (Updated)"
```

#### `snx goals delete ID`

```bash
snx goals delete 5 --yes
```

---

### fields

Manage custom fields for contacts and opportunities.

#### `snx fields list`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--entity` | `-e` | `contact` | Entity type: `contact` or `opportunity`. |

```bash
snx fields list
snx fields list --entity opportunity
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 30,
      "name": "lead_source",
      "label": "Lead Source",
      "type": 0,
      "isSystem": false,
      "isReadOnly": false,
      "isRequired": false,
      "isDropDown": true,
      "multiSelect": false,
      "defaultValue": "",
      "options": ["Web", "Referral", "Trade Show", "Cold Call"]
    }
  ]
}
```

**Field type mapping:**

| Type Code | Name | Description |
|-----------|------|-------------|
| `0` | `character` | Free text |
| `1` | `currency` | Money amount |
| `2` | `date` | Date |
| `3` | `numeric` | Number |
| `4` | `phone` | Phone number |
| `5` | `time` | Time |
| `6` | `checkbox` | Boolean |
| `7` | `percentage` | Percentage |
| `8` | `image` | Image URL |

#### `snx fields create`

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--entity` | `-e` | No | `contact` | `contact` or `opportunity`. |
| `--name` | `-n` | **Yes** | | Internal field name. |
| `--label` | `-l` | No | | Display label. |
| `--type` | `-t` | No | `character` | Field type (see table above). |
| `--required` | | No | `false` | Mark as required. |
| `--dropdown` | | No | `false` | Make it a dropdown. |
| `--multi-select` | | No | `false` | Allow multiple values. |
| `--default` | | No | | Default value. |
| `--options` | | No | | Comma-separated dropdown options. |

```bash
# Simple text field
snx fields create --name "lead_source" --label "Lead Source"

# Dropdown field with options
snx fields create \
  --name "industry" \
  --label "Industry" \
  --dropdown \
  --options "Technology,Manufacturing,Healthcare,Finance,Other"

# Opportunity currency field
snx fields create --entity opportunity --name "projected_revenue" --type currency

# Multi-select field
snx fields create --name "interests" --label "Interests" --dropdown --multi-select \
  --options "Product A,Product B,Product C"
```

---

### templates

Manage email templates (campaigns).

#### `snx templates list`

| Option | Default | Description |
|--------|---------|-------------|
| `--sort-by` | | Sort field. |
| `--sort-desc` | `false` | Sort descending. |
| `--mode` | | Filter: `bulk` or `triggered`. |

```bash
snx templates list
snx templates list --mode bulk
```

#### `snx templates get ID`

```bash
snx --json templates get 42
```

```json
{
  "id": 42,
  "name": "February Newsletter",
  "objective": "Monthly product updates",
  "status": "sent",
  "mode": "bulk",
  "scheduleAt": "2026-02-15T09:00:00Z",
  "segmentId": 7,
  "trackingHost": "track.salesnex.us",
  "createdAt": "2026-02-10T10:00:00Z",
  "updatedAt": "2026-02-15T09:05:00Z"
}
```

#### `snx templates stats ID`

Get send/open/click statistics for a template.

```bash
snx --json templates stats 42
```

```json
{
  "sent": 1250,
  "opens": 487,
  "clicks": 134,
  "bounces": 12,
  "unsubscribes": 3,
  "complaints": 0
}
```

#### `snx templates create`

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--name` | `-n` | **Yes** | | Template name. |
| `--objective` | | No | | Campaign objective. |
| `--mode` | | No | `bulk` | `bulk` or `triggered`. |
| `--segment-id` | | No | | Target segment ID. |

```bash
snx templates create --name "March Newsletter" --mode bulk --segment-id 7
```

#### `snx templates update ID`

```bash
snx templates update 42 --name "February Newsletter (Final)" --status "draft"
```

#### `snx templates delete ID`

```bash
snx templates delete 42 --yes
```

---

### reports

Manage saved reports.

#### `snx reports list`

```bash
snx reports list
```

#### `snx reports get ID`

```bash
snx --json reports get 15
```

```json
{
  "id": 15,
  "title": "Q1 Pipeline Summary",
  "specJson": "{\"type\":\"pipeline\",\"goalId\":5}",
  "narrativeJson": null,
  "isPublic": true,
  "createdAt": "2026-01-05T10:00:00Z",
  "lastRunAt": "2026-02-25T08:00:00Z"
}
```

#### `snx reports create`

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--title` | `-t` | **Yes** | Report title. |
| `--spec` | | No | Report spec as JSON string. |
| `--public` | | No | Make report visible to all users. |

```bash
snx reports create --title "Q1 Pipeline Summary" --public
```

#### `snx reports update ID`

```bash
snx reports update 15 --title "Q1 Pipeline Summary (Final)" --public
```

#### `snx reports delete ID`

```bash
snx reports delete 15 --yes
```

---

### lookups

Manage lookups (saved searches), segments (filter conditions), and layouts (column configs).

#### Lookups

```bash
snx lookups list                         # List all lookups
snx lookups get 7                        # Get a specific lookup
snx lookups create --name "Hot Leads"    # Create a lookup
```

**JSON output for `snx lookups get`:**

```json
{
  "id": 7,
  "name": "Hot Leads",
  "segmentId": 12,
  "layoutId": 3,
  "segment": { "id": 12, "name": "..." },
  "layout": { "id": 3, "name": "..." }
}
```

#### Segments (lookups segments)

Segments define filter conditions for contact lists.

```bash
snx lookups segments list                # List all segments
snx lookups segments get 12              # Get a segment
snx lookups segments create --name "Active in Texas" --spec '{"conditions": [...]}'
snx lookups segments update 12 --name "Active in TX (Updated)"
```

**Segment condition operators:** `equals`, `not_equals`, `gt`, `ge`, `lt`, `le`, `contains`, `not_contains`, `starts_with`, `ends_with`, `at`, `is_blank`

#### Layouts (lookups layouts)

Layouts configure which columns appear in a lookup view.

```bash
snx lookups layouts list
snx lookups layouts get 3
snx lookups layouts create --name "Compact View" --spec '{"columns": [...]}'
snx lookups layouts update 3 --name "Compact View (v2)"
```

---

### docs (documents)

Manage documents attached to contacts, groups, or opportunities.

#### `snx docs list`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | | `1` | Page number. |
| `--page-size` | | `20` | Results per page. |
| `--contact-id` | `-c` | | Filter by contact. |
| `--group-id` | `-g` | | Filter by group. |
| `--opportunity-id` | `-o` | | Filter by opportunity. |
| `--scope` | | `own` | `own` or `all`. |
| `--all` | `-a` | `false` | Fetch all pages. |

```bash
snx docs list --contact-id 101
```

#### `snx docs get ID`

```bash
snx --json docs get 300
```

```json
{
  "id": 300,
  "userId": 3,
  "contactId": 101,
  "groupId": null,
  "opportunityId": null,
  "description": "Signed contract",
  "originalFileName": "contract-2026.pdf",
  "mime": "application/pdf",
  "size": 245760,
  "tags": "contract,signed",
  "sourceUrl": "https://...",
  "sourceType": "url",
  "createdAt": "2026-02-20T10:00:00Z"
}
```

#### `snx docs create`

Create a document by importing from a URL.

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--url` | | **Yes** | URL to import. |
| `--description` | `-d` | No | Document description. |
| `--contact-id` | `-c` | No | Attach to contact. |
| `--group-id` | `-g` | No | Attach to group. |
| `--opportunity-id` | `-o` | No | Attach to opportunity. |
| `--tags` | | No | Comma-separated tags. |

```bash
snx docs create --url "https://example.com/proposal.pdf" --contact-id 101 --description "Q1 Proposal" --tags "proposal,q1"
```

#### `snx docs delete ID`

```bash
snx docs delete 300 --yes
```

---

### forms

Manage web forms for lead capture.

#### `snx forms list`

```bash
snx forms list
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 50,
      "name": "Contact Us",
      "slug": "contact-us",
      "status": "published",
      "isWiretap": false,
      "createdAt": "2025-12-01T10:00:00Z"
    }
  ]
}
```

#### `snx forms get ID`

```bash
snx forms get 50
```

#### `snx forms create`

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--name` | `-n` | **Yes** | Form name. |
| `--slug` | | No | URL slug. |
| `--redirect-url` | | No | Redirect URL after submission. |
| `--settings` | | No | Settings as JSON string. |

```bash
snx forms create --name "Contact Us" --slug "contact-us" --redirect-url "https://acme.com/thanks"
```

#### `snx forms update ID`

```bash
snx forms update 50 --name "Contact Us (v2)"
```

#### `snx forms delete ID`

```bash
snx forms delete 50 --yes
```

#### `snx forms embed ID`

Get the HTML embed code snippet for a published form.

```bash
snx forms embed 50
```

#### `snx forms unpublish ID`

Take a form offline.

```bash
snx forms unpublish 50
```

---

### users

List account users (read-only).

#### `snx users list`

```bash
snx users list
```

**JSON output:**

```json
{
  "data": [
    {
      "id": 3,
      "username": "john@acme.com",
      "email": "john@acme.com",
      "isActive": true,
      "securityLevel": "Admin"
    }
  ]
}
```

#### `snx users get ID`

```bash
snx users get 3
```

---

## Pagination

Most `list` commands are paginated. Two mechanisms are available:

### Manual pagination

```bash
snx contacts list --page 1 --page-size 50
snx contacts list --page 2 --page-size 50
```

### Auto-pagination (`--all`)

Use `--all` to automatically fetch every page and return the complete dataset:

```bash
snx contacts list --all --json
```

This iterates with `pageSize=100` until all records are retrieved. Useful for exports and AI agent workflows.

> **Limits:** `--page-size` max is 100 for most endpoints, 200 for tasks.

---

## Custom Fields

Contacts and opportunities support custom fields. These appear in the `customFields` object in JSON output.

### Setting custom fields on create/update

Use `--custom-field` (or `-F`) one or more times:

```bash
snx contacts create --first-name "Jane" \
  --custom-field "lead_source=Web" \
  --custom-field "industry=Tech" \
  --custom-field "score=85"
```

### Auto-creation

If a custom field name doesn't exist yet, the SalesNexus API **automatically creates it** as a Character type field. To create fields with specific types (dropdown, currency, etc.) first use `snx fields create`.

### Reading custom fields

Custom fields are included in all `get` and `list` JSON output:

```json
{
  "id": 101,
  "firstName": "Jane",
  "customFields": {
    "lead_source": "Web",
    "industry": "Tech",
    "score": "85"
  }
}
```

---

## Batch Operations

Contacts and opportunities support batch (bulk) operations.

### Selection modes

| Mode | Flag | Description |
|------|------|-------------|
| By IDs | `--ids "1,2,3"` | Explicit comma-separated list. |
| By Lookup | `--lookup-id 7` | All contacts matching a saved lookup/search. |

### Batch update

```bash
# Update specific contacts
snx contacts batch-update --ids "101,102,103" --field "status=Active"

# Update all contacts in a lookup
snx contacts batch-update --lookup-id 7 --field "status=Inactive" --field "source=Archive"
```

### Batch delete

```bash
snx contacts batch-delete --ids "101,102,103" --yes
snx contacts batch-delete --lookup-id 7 --yes
```

### Response

```json
{
  "successCount": 3,
  "deletedCount": 3,
  "opportunitiesDeletedCount": 0,
  "failedIds": []
}
```

---

## AI Agent Integration Guide

The SalesNexus CLI is purpose-built for use by AI coding agents (GitHub Copilot, Claude Code, Cursor, Windsurf, etc.). Here's how to integrate it.

### Auto-JSON detection

When an AI agent runs `snx` via subprocess, stdout is **not a TTY**, so the CLI automatically outputs JSON — no `--json` flag needed. Status messages (like "Contact 101 created.") go to **stderr**, keeping stdout clean for parsing.

### Recommended agent workflow

```bash
# 1. Check connectivity
snx ping

# 2. Discover the account structure
snx goals list          # pipelines & stages
snx fields list         # available fields
snx users list          # team members

# 3. Search for contacts
snx contacts list --search "Acme Corp"

# 4. Get full details
snx contacts get 101

# 5. Create/update records
snx contacts create --first-name "New" --last-name "Lead" --email "lead@co.com"
snx notes create --contact-id 101 --text "AI: Identified as high-value lead"

# 6. Bulk operations
snx contacts batch-update --ids "101,102" --field "status=Qualified"
```

### Composing commands (bash)

```bash
# Create a contact and immediately add a note
ID=$(snx contacts create --first-name "Jane" --email "jane@co.com" | jq -r '.id')
snx notes create --contact-id "$ID" --text "Auto-created by agent"

# Export all contacts to CSV
snx --csv contacts list --all > contacts_export.csv

# Find contacts without email and update them
snx contacts list --all | jq -r '.data[] | select(.email == null) | .id' | while read id; do
  snx contacts update "$id" --custom-field "needs_email=true"
done

# Get open opportunity value
snx opps list --all | jq '[.data[].amount // 0] | add'
```

### Composing commands (PowerShell)

```powershell
# Create a contact and capture ID
$result = snx contacts create --first-name "Jane" --email "jane@co.com" | ConvertFrom-Json
snx notes create --contact-id $result.id --text "Auto-created"

# List contacts as objects
$contacts = snx contacts list --all | ConvertFrom-Json
$contacts.data | Where-Object { $_.state -eq "TX" } | Format-Table

# Export to CSV
snx --csv contacts list --all | Out-File contacts.csv
```

### Using in CI/CD

```yaml
# GitHub Actions example
env:
  SALESNEXUS_API_KEY: ${{ secrets.SALESNEXUS_API_KEY }}

steps:
  - run: pip install salesnexus-cli
  - run: snx ping
  - run: snx contacts list --all --json > contacts.json
```

### MCP server note

SalesNexus also provides an MCP (Model Context Protocol) server for deeper AI integration with 47 tools and 34 resources. The CLI wraps the **public REST API** (stable, versioned), while MCP is used for real-time AI chat workflows. Both can complement each other.

---

## Error Handling & Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success. |
| `1` | Error (API error, auth failure, bad input, etc.). |

### Error messages

Errors print to **stderr** in a consistent format:

```
Error: HTTP 401: Invalid or expired API key. Run `snx auth login` to configure.
Error: HTTP 404: Resource not found.
Error: HTTP 429: Rate limit exceeded. Try again later.
Error: HTTP 409: Field 'lead_source' already exists.
```

The CLI automatically retries on transient failures (HTTP 429, 502, 503, 504) with exponential backoff, up to 3 attempts.

### JSON error output

When `--json` is active, errors still print to stderr (not stdout), so your JSON parsing pipeline won't break.

---

## Rate Limits

The SalesNexus API enforces rate limits:

| Limit | Value |
|-------|-------|
| Requests per hour | **10,000** per account |
| Queue depth | 2 requests |

When rate-limited, the CLI waits using the `Retry-After` header and retries automatically.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SALESNEXUS_API_KEY` | API key (overrides config file). |
| `SALESNEXUS_BASE_URL` | Base URL (overrides config file). Default: `https://api.salesnex.us`. Set to `https://api-beta.salesnex.us` for beta. |
| `SALESNEXUS_PROFILE` | Profile name to use (overrides `active_profile` in config). |
| `NO_COLOR` | Disable colored output (respected by rich). |

---

## Shell Completions

Install tab completion for your shell:

```bash
# Auto-detect shell
snx --install-completion

# Or show the completion script without installing
snx --show-completion
```

Supports: **bash**, **zsh**, **fish**, **PowerShell**.

After installing, restart your shell or source the config file. Then:

```bash
snx con<TAB>        → snx contacts
snx contacts cr<TAB> → snx contacts create
snx contacts create --<TAB>  → --first-name  --last-name  --email  ...
```

---

## Development

### Setup

```bash
cd salesnexus-cli
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Project structure

```
salesnexus-cli/
├── pyproject.toml              # Package config, "snx" entry point
├── README.md                   # This file
├── src/salesnexus_cli/
│   ├── __init__.py             # Version
│   ├── main.py                 # Typer app, global options, command registration
│   ├── config.py               # ~/.salesnexus/config.toml profile management
│   ├── client.py               # httpx wrapper (auth, retry, errors)
│   ├── output.py               # Dual formatter: rich tables / JSON / CSV
│   ├── pagination.py           # --all auto-pagination helper
│   └── commands/
│       ├── auth.py             # login, status, switch, list, logout
│       ├── contacts.py         # CRUD + batch + search
│       ├── opportunities.py    # CRUD + batch
│       ├── tasks.py            # CRUD + date filters
│       ├── notes.py            # CRUD
│       ├── goals.py            # CRUD (pipelines & stages)
│       ├── fields.py           # list + create (contact & opp)
│       ├── templates.py        # CRUD + stats
│       ├── reports.py          # CRUD
│       ├── lookups.py          # lookups + segments + layouts
│       ├── documents.py        # list + get + create-from-url + delete
│       ├── forms.py            # CRUD + embed + unpublish
│       ├── users.py            # list + get (read-only)
│       └── ping.py             # connectivity check
└── tests/
```

### Adding a new command

1. Create `src/salesnexus_cli/commands/mycommand.py`.
2. Define a `typer.Typer()` app with commands.
3. Register in `main.py`: `app.add_typer(mycommand.app, name="mycommand")`.

---

## Troubleshooting

### "snx" is not recognized

The Python Scripts directory is not on your PATH. Add it:

- **Windows:** `$env:PATH += ";$env:LOCALAPPDATA\...\Python3XX\Scripts"`
- **macOS/Linux:** `export PATH="$HOME/.local/bin:$PATH"`

Or run via: `python -m salesnexus_cli.main`

### "No API key configured"

Run `snx auth login --api-key sn_live_...` to save your key, or set `SALESNEXUS_API_KEY` environment variable.

### "Invalid or expired API key"

Your API key may have expired or been revoked. Generate a new one from SalesNexus Settings → API Keys.

### "Rate limit exceeded"

The CLI automatically retries, but if you're seeing this persistently, you're exceeding 10,000 requests/hour. Space out your requests or contact support.

### Timeout errors

The default timeout is 30 seconds. For large exports (`--all` with many pages), this should be sufficient per request. If you experience timeouts, check your network connection.

### SSL/TLS errors

If you're behind a corporate proxy, you may need to set `SSL_CERT_FILE` or `REQUESTS_CA_BUNDLE` environment variables, or use `--base-url` with your proxy URL.

---

## License

MIT
