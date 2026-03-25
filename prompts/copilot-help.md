# GitHub Copilot CLI Help

**GitHub Copilot CLI** — An AI-powered coding assistant.

Start an interactive session to chat with Copilot, or use `-p`/`--prompt` for non-interactive scripting. Copilot can edit files, run shell commands, search your codebase, and more — all with configurable permissions.

## Usage

```
copilot [options] [command]
```

Run `copilot <command> --help` for details on any subcommand.

---

## Options

### Session & Model

| Option | Description |
|--------|-------------|
| `--effort, --reasoning-effort <level>` | Set the reasoning effort level: `low`, `medium`, `high`, `xhigh` |
| `--model <model>` | Set the AI model to use |
| `--agent <agent>` | Specify a custom agent to use |

### Interactive Mode

| Option | Description |
|--------|-------------|
| `-i, --interactive <prompt>` | Start interactive mode and automatically execute this prompt |
| `--continue` | Resume the most recent session |
| `--resume[=sessionId]` | Resume from a previous session (optionally specify session ID or task ID) |
| `--autopilot` | Enable autopilot continuation in prompt mode |
| `--max-autopilot-continues <count>` | Maximum number of continuation messages in autopilot mode (default: unlimited) |

### Non-Interactive Mode

| Option | Description |
|--------|-------------|
| `-p, --prompt <text>` | Execute a prompt in non-interactive mode (exits after completion) |
| `-s, --silent` | Output only the agent response (no stats), useful for scripting with `-p` |
| `--output-format <format>` | Output format: `text` (default) or `json` (JSONL, one JSON object per line) |
| `--stream <mode>` | Enable or disable streaming mode: `on`, `off` |

### Permissions & Security

| Option | Description |
|--------|-------------|
| `--allow-all` | Enable all permissions (equivalent to `--allow-all-tools --allow-all-paths --allow-all-urls`) |
| `--yolo` | Enable all permissions (equivalent to `--allow-all-tools --allow-all-paths --allow-all-urls`) |
| `--allow-all-tools` | Allow all tools to run automatically without confirmation; required for non-interactive mode (env: `COPILOT_ALLOW_ALL`) |
| `--allow-all-paths` | Disable file path verification and allow access to any path |
| `--allow-all-urls` | Allow access to all URLs without confirmation |
| `--allow-tool[=tools...]` | Tools the CLI has permission to use; will not prompt for permission |
| `--deny-tool[=tools...]` | Tools the CLI does not have permission to use; will not prompt for permission |
| `--allow-url[=urls...]` | Allow access to specific URLs or domains |
| `--deny-url[=urls...]` | Deny access to specific URLs or domains (takes precedence over `--allow-url`) |
| `--no-ask-user` | Disable the ask_user tool (agent works autonomously without asking questions) |
| `--secret-env-vars[=vars...]` | Environment variable names whose values are stripped from shell and output (e.g., `--secret-env-vars=MY_KEY,OTHER_KEY`) |

### File & Directory Access

| Option | Description |
|--------|-------------|
| `--add-dir <directory>` | Add a directory to the allowed list for file access (can be used multiple times) |
| `--disallow-temp-dir` | Prevent automatic access to the system temporary directory |

### Display & Output

| Option | Description |
|--------|-------------|
| `--no-color` | Disable all color output |
| `--plain-diff` | Disable rich diff rendering (syntax highlighting via diff tool specified by git config) |
| `--alt-screen[=value]` | Use the terminal alternate screen buffer (`on`/`off`) |
| `--no-alt-screen` | Disable the terminal alternate screen buffer |
| `--mouse[=value]` | Enable mouse support in alt screen mode (`on`/`off`) |
| `--no-mouse` | Disable mouse support in alt screen mode |
| `--screen-reader` | Enable screen reader optimizations |
| `--banner` | Show the startup banner |

### Configuration

| Option | Description |
|--------|-------------|
| `--config-dir <directory>` | Set the configuration directory (default: `~/.copilot`) |
| `--log-dir <directory>` | Set log file directory (default: `~/.copilot/logs/`) |
| `--log-level <level>` | Set the log level: `none`, `error`, `warning`, `info`, `debug`, `all`, `default` |
| `--no-custom-instructions` | Disable loading of custom instructions from `AGENTS.md` and related files |

### MCP Server Configuration

| Option | Description |
|--------|-------------|
| `--acp` | Start as Agent Client Protocol server |
| `--add-github-mcp-tool <tool>` | Add a tool to enable for the GitHub MCP server (can be used multiple times). Use `*` for all tools |
| `--add-github-mcp-toolset <toolset>` | Add a toolset to enable for the GitHub MCP server (can be used multiple times). Use `all` for all toolsets |
| `--enable-all-github-mcp-tools` | Enable all GitHub MCP server tools instead of the default CLI subset |
| `--additional-mcp-config <json>` | Additional MCP servers configuration as JSON string or file path (prefix with `@`) |
| `--disable-builtin-mcps` | Disable all built-in MCP servers (currently: `github-mcp-server`) |
| `--disable-mcp-server <server-name>` | Disable a specific MCP server (can be used multiple times) |

### Environment & Shell

| Option | Description |
|--------|-------------|
| `--bash-env[=value]` | Enable BASH_ENV support for bash shells (`on`/`off`) |
| `--no-bash-env` | Disable BASH_ENV support for bash shells |

### Updates & Info

| Option | Description |
|--------|-------------|
| `--no-auto-update` | Disable downloading CLI update automatically (disabled by default in CI environments) |
| `--experimental` | Enable experimental features |
| `--no-experimental` | Disable experimental features |

### Plugins & Extensions

| Option | Description |
|--------|-------------|
| `--plugin-dir <directory>` | Load a plugin from a local directory (can be used multiple times) |

### Session Sharing

| Option | Description |
|--------|-------------|
| `--share[=path]` | Share session to markdown file after completion (default: `./copilot-session-<id>.md`) |
| `--share-gist` | Share session to a secret GitHub gist after completion in non-interactive mode |

### General

| Option | Description |
|--------|-------------|
| `-h, --help` | Display help for command |
| `-v, --version` | Show version information |

---

## Commands

| Command | Description |
|---------|-------------|
| `help [topic]` | Display help information |
| `init` | Initialize Copilot instructions |
| `login [options]` | Authenticate with Copilot |
| `plugin` | Manage plugins |
| `update` | Download the latest version |
| `version` | Display version information |

---

## Help Topics

| Topic | Description |
|-------|-------------|
| `commands` | Interactive Mode Commands |
| `config` | Configuration Settings |
| `environment` | Environment Variables |
| `logging` | Logging |
| `permissions` | Permissions |

---

## Examples

### Basic Usage

```bash
# Start interactive mode
copilot

# Start interactive mode and automatically execute a prompt
copilot -i "Fix the bug in main.js"

# Execute a prompt in non-interactive mode (exits after completion)
copilot -p "Fix the bug in main.js" --allow-all-tools

# Enable all permissions with a single flag
copilot -p "Fix the bug in main.js" --allow-all
copilot -p "Fix the bug in main.js" --yolo
```

### Models & Configuration

```bash
# Start with a specific model
copilot --model gpt-5.2
```

### Session Management

```bash
# Resume the most recent session
copilot --continue

# Resume a previous session using session picker
copilot --resume

# Resume a specific session by ID
copilot --resume=<session-id>

# Start a new session with a specific UUID
copilot --resume=0cb916db-26aa-40f2-86b5-1ba81b225fd2

# Resume with auto-approval
copilot --allow-all-tools --resume
```

### File & Path Permissions

```bash
# Allow access to additional directory
copilot --add-dir /home/user/projects

# Allow multiple directories
copilot --add-dir ~/workspace --add-dir /tmp

# Disable path verification (allow access to any path)
copilot --allow-all-paths
```

### Tool & Permissions Management

```bash
# Allow all git commands except git push
copilot --allow-tool='shell(git:*)' --deny-tool='shell(git push)'

# Allow all file editing
copilot --allow-tool='write'

# Allow all but one specific tool from MCP server with name "MyMCP"
copilot --deny-tool='MyMCP(denied_tool)' --allow-tool='MyMCP'
```

### URL Permissions

```bash
# Allow GitHub API access (defaults to HTTPS)
copilot --allow-url=github.com

# Deny access to specific domain over HTTPS
copilot --deny-url=https://malicious-site.com
copilot --deny-url=malicious-site.com

# Allow all URLs without confirmation
copilot --allow-all-urls
```

### Repository Setup

```bash
# Initialize Copilot instructions for a repository
copilot init
```

---

## Learn More

- Use `copilot <command> --help` for more information about a command
- Read the documentation at [https://docs.github.com/copilot/how-tos/copilot-cli](https://docs.github.com/copilot/how-tos/copilot-cli)