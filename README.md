# Basic Agents

Some really basic agents

`run-command` - Runs commands on your WSL thing
`web-search` - Does what it says on the tin
`change-directory` - sets the working directory for linux

Configure it with a `claude_desktop_config.json` file that looks a little like this (you'll almost certainly need to replace $HOME with your actual home directory on WSL). It's probably 10x easier to configure on a Mac!

```
{
  "mcpServers": {
    "shell": {
      "command": "wsl",
      "args": [
        "$HOME/.local/bin/uv",
        "--directory",
        "$HOME/code/local-dev/shell",
        "run",
        "shell"
      ]
    }
  }
}
```


  