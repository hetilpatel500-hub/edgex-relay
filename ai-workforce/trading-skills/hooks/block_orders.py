#!/usr/bin/env python3
"""PreToolUse guard: while this plugin is enabled, Claude cannot call a tool
that places, changes or cancels an order (any MCP server, any broker).

Reads the hook payload on stdin. Exit code 2 blocks the call and tells
Claude why; exit 0 lets it through. Read-only tools (bars, quotes, news,
calendars, account balances) are never blocked.
"""
import json, re, sys

ORDER = re.compile(
    r'(^|_)(place|submit|send|create|cancel|revoke|replace|modify|amend|update|edit)_([a-z0-9]+_)*(order|instruction)s?(_|$)'
    r'|(^|_)(close|liquidate|flatten|exercise)_([a-z0-9]+_)*(position|order|option)s?(_|$)'
    r'|^(buy|sell)(_|$)|_(buy|sell)$',
    re.I)


def blocked(name):
    tool = name.split('__')[-1] if name.startswith('mcp__') else ''
    return bool(tool) and bool(ORDER.search(tool))


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    name = payload.get('tool_name', '')
    if blocked(name):
        print(f'Blocked by edgex-trading-skills: "{name}" can place, change or cancel orders. These skills are '
              'analysis only; the trader places any trade themselves, outside Claude.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
