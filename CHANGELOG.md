# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-12

### Added

- **Label**: Added `update_label` tool to safely update a label's title, description, and color (using a Read-Modify-Write flow).
- **Label**: Added `delete_label` tool to permanently delete a label.
- Added `labels` field to the `Task` model to expose the list of labels returned in API responses.

### Fixed

- **Incorrect HTTP Methods (Root cause of "405 Method Not Allowed")**
  - Adjusted API requests to follow Vikunja's custom conventions where "Create = PUT" and "Update = POST".
  - Changed the method from `POST` to `PUT` for `create_label`, `create_project`, `create_task`, and `add_comment_to_task`.
- **Color field name in `create_label` / `update_label`**
  - Renamed the request body key from `color` to `hex_color` to match the Vikunja API specifications.
  - Aligned the field name in the `Label` model from `color` to `hex_color`.
- **Ignore-bug of `done=False` in `update_task`**
  - Fixed an issue where passing `done=False` was skipped due to a falsy check; it now checks for `is not None` explicitly.
  - Fixed general parameter checking to ensure `False` and other falsy values are not ignored.
- **Improved safety of Read-Modify-Write in `update_task` using a whitelist**
  - Replaced the previous `model_dump(by_alias=True)` approach which sent all nested fields (like labels and assignees), posing a risk of unintended overrides on the API side.
  - Re-implemented payload generation using a strict whitelist of writable scalar fields.

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
