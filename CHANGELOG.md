# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-12

### Added

- Initial release of the `rmc-vikunja-mcp` server.
- Full Model Context Protocol (MCP) server implementation targeting the Vikunja API.
- Support for various resources:
  - **User**: `get_user_info`, `search_users`
  - **Project**: `list_projects`, `create_project`, `get_project`, `delete_project`
  - **Task**: `get_task`, `list_tasks`, `list_tasks_global`, `create_task`, `update_task`, `delete_task`
  - **Label**: `list_labels`, `create_label`, `add_label_to_task`, `remove_label_from_task`
  - **Assignee**: `assign_user_to_task`, `unassign_user_from_task`
  - **Comment**: `list_task_comments`, `add_comment_to_task`
- Robust Read-Modify-Write (RMW) flow for `update_task` to prevent resetting unspecified properties.
- Dynamic models with `extra="ignore"` to maintain stability when the Vikunja API returns newer fields.
- Fully asynchronous client and server architecture using `httpx` and `mcp` SDK.
- Complete asynchronous test suite with detailed mock-server fixtures.
