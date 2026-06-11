# rmc-vikunja-mcp

A **Model Context Protocol (MCP)** server that connects LLM-based assistants to the [Vikunja](https://vikunja.io/) task-management platform.

## Features

| Category      | Tools                                                                            |
|---------------|----------------------------------------------------------------------------------|
| **User**      | `get_user_info`, `search_users`                                                  |
| **Project**   | `list_projects`, `create_project`, `get_project`, `delete_project`               |
| **Task**      | `get_task`, `list_tasks`, `list_tasks_global`, `create_task`, `update_task`, `delete_task` |
| **Label**     | `list_labels`, `create_label`, `add_label_to_task`, `remove_label_from_task`      |
| **Assignee**  | `assign_user_to_task`, `unassign_user_from_task`                                 |
| **Comment**   | `list_task_comments`, `add_comment_to_task`                                      |

### Key design decisions

- **Read-Modify-Write for task updates** – Vikunja's `POST /tasks/{id}` endpoint resets fields absent from the request body. `update_task` therefore fetches the current state, merges the caller's changes, strips read-only timestamps, and posts the result back.
- **`extra="ignore"` on Pydantic models** – Unknown fields returned by future API versions are silently discarded instead of causing validation failures.

## Quick start

### Prerequisites

- Python ≥ 3.14
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A running Vikunja instance with an API token

### Configuration

Create a `.env` file (or export the variables directly):

```dotenv
VIKUNJA_URL=https://your-vikunja-instance.example.com
VIKUNJA_TOKEN=your-api-token
```

### Running the server

You can run the server directly without manual installation using `uvx` (recommended):

```bash
uvx rmc-vikunja-mcp
```

Alternatively, you can install it via pip and run it using the CLI entry-point:

```bash
uv pip install rmc-vikunja-mcp
vikunja-mcp
# or
python -m vikunja_mcp
```

### MCP client configuration (e.g. Claude Desktop)

#### Using `uvx` (Recommended)

This method does not require prior installation:

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "uvx",
      "args": [
        "rmc-vikunja-mcp"
      ],
      "env": {
        "VIKUNJA_URL": "https://your-vikunja-instance.example.com",
        "VIKUNJA_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### Using globally installed package

If you installed the package via `pip` or `uv pip install`:

```json
{
  "mcpServers": {
    "vikunja": {
      "command": "vikunja-mcp",
      "env": {
        "VIKUNJA_URL": "https://your-vikunja-instance.example.com",
        "VIKUNJA_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/rmc8/rmc_vikunja_mcp.git
cd rmc_vikunja_mcp
uv sync

# Run checks
uv run ruff check          # linter
uv run mypy src tests      # type checker (strict mode)
uv run pytest -v           # tests
```

## License

MIT