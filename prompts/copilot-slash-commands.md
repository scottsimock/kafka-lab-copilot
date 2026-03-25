| Command | Description |
| --- | --- |
| `/add-dir <directory>` | Add a directory to the allowed list for file access |
| `/agent` | Browse and select from available agents (if any) |
| `/allow-all`, `/yolo` | Enable all permissions (tools, paths, and URLs) |
| `/changelog [summarize] [version \\| last <N> \\| ...]` | Display changelog for CLI versions. Add `summarize` to get an AI summary. |
| `/clear`, `/new` | Clear the conversation history |
| `/compact` | Summarize conversation history to reduce context window usage |
| `/context` | Show context window token usage and visualization |
| `/copy` | Copy the last response to the clipboard |
| `/cwd`, `/cd [directory]` | Change working directory or show current directory |
| `/delegate [prompt]` | Send this session to GitHub and Copilot will create a PR |
| `/diff` | Review the changes made in the current directory |
| `/exit`, `/quit` | Exit the CLI |
| `/experimental [on\\|off\\|show]` | Show available experimental features, or enable/disable experimental mode |
| `/share [file\\|gist] [session\\|research] [path]` | Share session or research report to markdown file or GitHub gist |
| `/feedback` | Provide feedback about the CLI |
| `/fleet [prompt]` | Enable fleet mode for parallel subagent execution |
| `/help` | Show help for interactive commands |
| `/ide` | Connect to an IDE workspace |
| `/init [suppress]` | Initialize Copilot instructions for this repository, or suppress the init suggestion |
| `/list-dirs` | Display all allowed directories for file access |
| `/login` | Log in to Copilot |
| `/logout` | Log out of Copilot |
| `/lsp [show\\|test\\|reload\\|help] [server-name]` | Manage language server configuration |
| `/mcp [show\\|add\\|edit\\|delete\\|disable\\|enable] [...]` | Manage MCP server configuration |
| `/model`, `/models [model]` | Select AI model to use |
| `/plan [prompt]` | Create an implementation plan before coding |
| `/pr [view\\|create\\|fix\\|auto]` | Operate on pull requests for the current branch |
| `/plugin [marketplace\\|install\\|uninstall\\|update ...]` | Manage plugins and plugin marketplaces |
| `/rename <name>` | Rename the current session (alias for `/session rename`) |
| `/reset-allowed-tools` | Reset the list of allowed tools |
| `/research <topic>` | Run deep research investigation using GitHub search and web sources |
| `/restart` | Restart the CLI, preserving the current session |
| `/resume [sessionId]` | Switch to a different session (optionally specify session ID or task ID) |
| `/review [prompt]` | Run code review agent to analyze changes |
| `/session`, `/sessions [info\\|checkpoints [n]\\|find ...]` | View and manage sessions. Use subcommands for details. |
| `/skills [list\\|info\\|add\\|remove\\|reload] [args ...]` | Manage skills for enhanced capabilities |
| `/tasks` | View and manage background tasks (subagents and shell sessions) |
| `/terminal-setup` | Configure terminal for multiline input support (shift+enter) |
| `/theme [default\\|dim\\|high-contrast\\|colorblind]` | View or set color mode |
| `/undo`, `/rewind` | Rewind the last turn and revert file changes |
| `/update` | Update the CLI to the latest version |
| `/usage` | Display session usage metrics and statistics |
| `/user [show\\|list\\|switch]` | Manage GitHub user list |
| `/version` | Display version information and check for updates |