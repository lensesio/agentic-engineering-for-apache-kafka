# Troubleshooting

General troubleshooting guide for agent skills in this repository. For skill-specific issues, see the Troubleshooting section in each skill's `SKILL.md`. Based on [Anthropic's skill guide, Chapter 5](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Skill Won't Upload

### "Could not find SKILL.md in uploaded folder"

**Cause**: File not named exactly `SKILL.md` (case-sensitive).

**Solution**: Rename the file to `SKILL.md` and verify with `ls -la`.

### "Invalid frontmatter"

**Cause**: YAML formatting issue in the `---` delimited block at the top of `SKILL.md`.

**Common mistakes**:

```yaml
# Wrong - missing delimiters
name: my-skill
description: Does things

# Wrong - unclosed quotes
---
name: my-skill
description: "Does things
---

# Correct
---
name: my-skill
description: Does things
---
```

### "Invalid skill name"

**Cause**: Name contains spaces or capitals.

```yaml
# Wrong
name: My Cool Skill

# Correct
name: my-cool-skill
```

## Skill Doesn't Trigger

**Symptom**: Skill never loads automatically when you ask a relevant question.

**Quick checklist**:
- Is the description too generic? ("Helps with projects" won't trigger reliably)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types if applicable?

**Debugging approach**: Ask Claude *"When would you use the [skill-name] skill?"* - Claude will quote the description back. Adjust based on what's missing.

**Solution**: Revise the `description` field to include specific trigger phrases. See any of the skills in this repo for examples of good descriptions with explicit trigger phrases.

## Skill Triggers Too Often

**Symptom**: Skill loads for unrelated queries.

**Solutions**:

1. **Add negative triggers**: Include "Do NOT use for X" in the description
2. **Be more specific**: Replace generic descriptions ("Processes documents") with specific ones ("Processes PDF legal documents for contract review")
3. **Clarify scope**: State what tool/service the skill targets

All skills in this repo already include negative triggers. See any `SKILL.md` for examples.

## MCP Connection Issues

**Symptom**: Skill loads but Lenses MCP tool calls fail.

**Checklist**:

1. **Verify MCP server is connected**
   - Cursor: Check MCP settings panel
   - Claude.ai: Settings > Extensions > Lenses
   - Claude Code: Check `~/.claude.json` (user) or `.claude/settings.json` (project) for MCP server config
   - Should show "Connected" status

2. **Check authentication**
   - Lenses API keys/tokens are valid and not expired
   - Proper permissions granted
   - Environment name matches what `list_environments` returns

3. **Test MCP independently** (without the skill)
   - Ask Claude: *"Use Lenses MCP to list environments"*
   - If this fails, the issue is the MCP connection not the skill

4. **Verify tool names**
   - Skill references the correct MCP tool names
   - Tool names are case-sensitive
   - Check the [Lenses MCP documentation](https://github.com/lensesio/lenses-mcp) for the latest tool names

## Instructions Not Followed

**Symptom**: Skill loads but Claude doesn't follow the workflow steps.

**Common causes and fixes**:

1. **Instructions too verbose** - Keep instructions concise. Use bullet points and numbered lists. Move detailed reference material to `references/` files (this repo already does this).

2. **Instructions buried** - Put critical instructions at the top. Use `## Important` or `## Critical` headers. Repeat key points if needed.

3. **Ambiguous language** - Be specific:

```markdown
# Bad
Make sure to validate things properly

# Good
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

4. **Model "laziness"** - Add explicit encouragement in your prompt (not in SKILL.md):

```
Take your time to do this thoroughly.
Quality is more important than speed.
Do not skip validation steps.
```

## Large Context Issues

**Symptom**: Skill seems slow or responses are degraded.

**Causes**:
- Skill content too large (over 5,000 words)
- Too many skills enabled simultaneously (more than 20-50)
- All content loaded inline instead of using progressive disclosure

**Solutions**:

1. **Optimise SKILL.md size** - Move detailed docs to `references/`. Link to references instead of inlining. Keep SKILL.md under 5,000 words. All skills in this repo are currently under 1,300 words.

2. **Reduce enabled skills** - If you have many skills enabled, consider selective enablement. Only enable what you need for the current task.

## Claude Code Plugin Install Issues

### `/plugin install kafka-skills@lensesio` fails with "marketplace not found"

**Cause**: The `lensesio` marketplace hasn't been added yet.

**Solution**: Run `/plugin marketplace add lensesio/agentic-engineering-for-apache-kafka` first, then retry the install. List configured marketplaces with `/plugin marketplace list`.

### Skills not available after install

**Cause**: Plugin skills are namespaced under the plugin name. They auto-trigger from natural-language requests, but explicit slash invocation requires the namespace.

**Solution**: Use `/kafka-skills:topic-audit` (and similar for the other six). Confirm install succeeded with `/plugin list` - you should see `kafka-skills@lensesio` enabled.

### `claude plugin validate` errors after editing the marketplace

**Cause**: Schema mismatch. As of Claude Code 2.1.x the validator rejects an unrecognised top-level `description` on the marketplace; it must live under `metadata`.

**Solution**: Move marketplace-level `description` (and `version`) under `"metadata": { ... }` per the official [marketplace schema](https://code.claude.com/docs/en/plugin-marketplaces#optional-fields).

### `/plugin update kafka-skills` fails with "Plugin not found"

**Cause**: When more than one marketplace is registered, the plain plugin name is ambiguous.

**Solution**: Use the namespaced form: `/plugin update kafka-skills@lensesio`.

### Auto-update fails for the GitHub-hosted marketplace

**Cause**: Background updates run without your interactive git credential helper, so private repos and rate-limited GitHub access can fail.

**Solution**: Set `GITHUB_TOKEN` (or `GH_TOKEN`) in your shell profile. See [Private repositories](https://code.claude.com/docs/en/plugin-marketplaces#private-repositories) for the full list of supported providers.

For more, see Anthropic's [Plugin marketplaces troubleshooting](https://code.claude.com/docs/en/plugin-marketplaces#troubleshooting).

## Kafka-Specific Issues

### Environment name not recognised

**Cause**: The environment name passed to the skill doesn't match any environment in Lenses.

**Solution**: Run `list_environments` via Lenses MCP to see available environment names. Environment names are case-sensitive.

### No topics / consumer groups / connectors returned

**Cause**: The environment exists but has no resources or the Lenses agent has restricted permissions.

**Solution**: Verify via the Lenses UI that the expected resources exist. Check that the Lenses service account has read access to the relevant resources.

### Schema Registry not available

**Cause**: Schema Registry is not configured in the Lenses environment.

**Solution**: This is a valid finding - skills like `schema-review` will report this as a governance gap rather than treating it as an error.
