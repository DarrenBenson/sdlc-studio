# Best Practices: Settings

## Checklist

Before considering a settings.json complete:

- [ ] File exists at `.claude/settings.json`
- [ ] Bash patterns use `:*` for prefix matching (not just `*`)
- [ ] Sensitive files denied (`.env`, secrets, credentials)
- [ ] Path patterns use correct prefix (`//` for absolute, `~` for home)
- [ ] No overly permissive rules without justification

## Structure

```json
{
  "permissions": {
    "allow": ["Rule1", "Rule2"],
    "ask": ["Rule3"],
    "deny": ["Rule4"]
  }
}
```

### Permission Precedence

Deny > Ask > Allow

## Bash Patterns

Bash rules use **prefix matching** with colon syntax:

| Pattern | Matches | Does NOT Match |
|---------|---------|----------------|
| `Bash(git :*)` | `git status`, `git commit -m "msg"` | - |
| `Bash(npm run test:*)` | `npm run test`, `npm run test:unit` | `npm run build` |
| `Bash(./scripts/*)` | `./scripts/deploy.sh` | `scripts/deploy.sh` |

### Common Mistake

```json
// WRONG - won't match properly
"Bash(git *)"
"Bash(python3 *)"

// CORRECT - use colon before asterisk
"Bash(git :*)"
"Bash(python3 :*)"
```

### Security Note

Bash patterns can be bypassed via:
- Variable expansion: `CMD=rm && $CMD -rf /`
- Option reordering: `curl -X GET http://site.com`
- Piping: `echo password | sudo -S rm -rf /`

Use as one layer of protection, not sole defence.

## File Path Patterns

Read and Edit rules use gitignore-style patterns:

| Pattern | Resolves To |
|---------|-------------|
| `path` or `./path` | Relative to CWD |
| `/path` | Relative to settings.json location |
| `//path` | Absolute filesystem root |
| `~/path` | User home directory |

### Examples

```json
{
  "permissions": {
    "allow": [
      "Read(src/**)",           // All files under src/
      "Edit(src/**/*.ts)",      // TypeScript files in src/
      "Read(~/.zshrc)"          // Home directory file
    ],
    "deny": [
      "Read(.env)",             // Block .env in CWD
      "Read(.env.*)",           // Block .env.local, etc.
      "Read(./secrets/**)",     // Block secrets directory
      "Read(//etc/passwd)"      // Block absolute path
    ]
  }
}
```

## Template

Minimal safe starting point:

```json
{
  "permissions": {
    "allow": [
      "Read(src/**)",
      "Edit(src/**)",
      "Bash(git :*)",
      "Bash(npm run :*)"
    ],
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(./secrets/**)",
      "Bash(sudo:*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

## Project-Specific Patterns

### Python Project

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 :*)",
      "Bash(pip :*)",
      "Bash(pytest :*)",
      "Bash(./scripts/*)"
    ]
  }
}
```

### Node Project

```json
{
  "permissions": {
    "allow": [
      "Bash(npm :*)",
      "Bash(npx :*)",
      "Bash(node :*)"
    ]
  }
}
```

### Engram Project

```json
{
  "permissions": {
    "allow": [
      "Read(engrams/**)",
      "Read(scenarios/**)",
      "Read(realities/**)",
      "Edit(engrams/**)",
      "Bash(git :*)",
      "Bash(python3 :*)",
      "Bash(./scripts/*)"
    ]
  }
}
```

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `Bash(git *)` | Missing colon, won't prefix match | `Bash(git :*)` |
| `Bash` (bare) | Allows all commands | List specific commands |
| No deny rules | Secrets accessible | Deny `.env`, `secrets/` |
| `Read` (bare) | Allows reading any file | Scope to project dirs |
| `//etc/**` in allow | System files exposed | Remove or be specific |

## Additional Options

### Default Mode

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

| Mode | Behaviour |
|------|-----------|
| `default` | Prompt on first use |
| `acceptEdits` | Auto-accept file edits |
| `plan` | Read-only, no execution |
| `bypassPermissions` | Skip all prompts (dangerous) |

### Additional Directories

```json
{
  "permissions": {
    "additionalDirectories": [
      "../shared-lib/",
      "~/common-config/"
    ]
  }
}
```

### Environment Variables

```json
{
  "env": {
    "NODE_ENV": "development",
    "DEBUG": "true"
  }
}
```

## Scope Hierarchy

Settings merge with this precedence (highest to lowest):

1. Enterprise managed (`/etc/claude-code/managed-settings.json`)
2. CLI arguments (`--dangerously-skip-permissions`)
3. Local project (`.claude/settings.local.json` - gitignored)
4. Shared project (`.claude/settings.json` - committed)
5. User settings (`~/.claude/settings.json`)

## Tool Reference

### Always Allowed (No Permission Needed)

- `Glob` - Find files by pattern
- `Grep` - Search file contents
- `Read` - Read file contents (unless denied)

### Require Permission

| Tool | Pattern Example |
|------|-----------------|
| `Edit` | `Edit(src/**)` |
| `Write` | `Write` or `Write(path)` |
| `Bash` | `Bash(command :*)` |
| `WebFetch` | `WebFetch(domain:example.com)` |
| `WebSearch` | `WebSearch` |
| MCP tools | `mcp__servername__*` |
