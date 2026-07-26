# Private outbound sender

This replaces Apple Mail scheduling with a Gmail API queue on the always-on Mac mini. It sends one
existing Gmail draft at a time, retains private state outside Git, retries transient failures, and
reconciles a draft's Gmail message ID before retrying so a worker crash cannot duplicate a send.

The service is paused by default. Planning does not edit or send drafts. Preparation requires a
valid business postal address, adds a commercial-message disclosure and reply-based opt-out to
each recipient-ready draft, and still leaves the queue paused. `resume` is a separate explicit
action.

## Private state

```text
~/.local/share/eastbayprojects/outbound-sender/
  queue.sqlite3
  service.env
  service.log
  service-error.log
```

The Gmail OAuth credential remains in the private Google Workspace MCP credentials directory.

## Schedule

The default campaign ramp is 10, 15, and 20 messages on its first three weekdays, then no more
than 25 per weekday. Messages are distributed from 9:30 a.m. through 3:30 p.m. Eastern. The
worker sends at most one due draft per minute and auto-pauses after five bounces or a 5% bounce
rate once at least 20 messages have been sent. It also pauses instead of burst-sending a backlog
when the oldest due message is more than two hours late.

## Commands

Run these on the Mac mini from `~/Projects/eastbayprojects`:

```sh
./scripts/run-outbound-sender.sh plan --start-date 2026-07-27
./scripts/run-outbound-sender.sh status

# Requires Nate's valid business street address or registered PO Box:
./scripts/run-outbound-sender.sh prepare \
  --postal-address='VALID BUSINESS POSTAL ADDRESS'

./scripts/run-outbound-sender.sh resume
./scripts/run-outbound-sender.sh pause --reason='manual review'
./scripts/run-outbound-sender.sh suppress person@example.com
```

If preparation or approval happens after the planned start, run `plan` again with a future
weekday before `resume`; the sender refuses to release a queue containing past-due messages.

## LaunchAgent

Install the checked-in template on the Mac mini:

```sh
mkdir -p ~/Library/LaunchAgents
sed -e "s|__HOME__|$HOME|g" \
    -e "s|__PROJECT_DIR__|$HOME/Projects/eastbayprojects|g" \
    outbound_sender/com.eastbayprojects.outbound-sender.plist.example \
    > ~/Library/LaunchAgents/com.eastbayprojects.outbound-sender.plist
launchctl bootstrap \
  "gui/$(id -u)" \
  ~/Library/LaunchAgents/com.eastbayprojects.outbound-sender.plist
```

The LaunchAgent can remain loaded while paused. The Air is not involved.
