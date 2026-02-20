# Example: Countdown with Durable Sleep (Python)

A countdown timer that demonstrates **durable sleep** - long pauses without consuming resources, surviving crashes and resuming exactly where it left off.

## What This Demonstrates

### Problem: Long-Running Timers
Traditional countdown timers keep a process running continuously, wasting resources during sleep periods. If the process crashes, you lose the countdown state.

### Solution: Durable Sleep
Resonate's durable sleep allows workflows to:
- Pause for extended periods (hours, days, weeks)
- Consume zero resources while sleeping
- Survive crashes and resume at the right time
- Send periodic notifications reliably

## Use Cases

This pattern applies to:
- **Scheduled reminders** - Meeting notifications, task deadlines
- **SLA monitors** - Alert if response not received in time
- **Rate limiting** - Enforce delays between operations
- **Periodic reports** - Daily/weekly/monthly automation
- **Countdown timers** - Track time until events

## How It Works

```python
def countdown(ctx: Context, count: int, interval, url: str):
    for i in range(count, 0, -1):
        # Send notification (durable)
        yield ctx.run(notify, message=f"Countdown: {i}", url=url)

        # Sleep for interval (process can exit here)
        yield ctx.sleep(interval)

    # Final notification
    yield ctx.run(notify, message="Countdown complete", url=url)
```

### What Happens on Each Iteration

1. **Send notification** - `ctx.run()` executes and checkpoints the result
2. **Sleep** - `ctx.sleep()` suspends the workflow, process can exit
3. **Resume** - Resonate wakes the workflow after the interval
4. **Repeat** - Continue from checkpoint without re-sending notifications

### Crash Recovery

If the process crashes during sleep:
- Workflow state is preserved in Resonate
- Resonate automatically resumes at the scheduled wake time
- No notifications are duplicated
- Countdown continues as if nothing happened

## Running the Example

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- ntfy.sh account or webhook URL

### Installation

```bash
# Install dependencies
uv sync
```

### Usage

```bash
# Start the countdown worker
uv run python countdown.py
```

Then trigger a countdown via the Resonate API or another process:

```bash
# Start 10-minute countdown with 1-minute intervals
curl -X POST http://localhost:8001/promises \
  -H "Content-Type: application/json" \
  -d '{
    "id": "countdown/demo",
    "timeout": 36000000,
    "data": {
      "func": "countdown",
      "args": [10, 60000, "https://ntfy.sh/your-topic"]
    }
  }'
```

**Parameters:**
- `count`: Number of countdown steps (10 = 10 notifications)
- `interval`: Milliseconds between steps (60000 = 1 minute)
- `url`: Webhook URL for notifications (ntfy.sh, Slack, etc.)

### Notification Format

Each notification sends JSON:
```json
{
  "message": "Countdown: 7"
}
```

## Configuration

### Environment Variables

Create a `.env` file:
```bash
RESONATE_URL=http://localhost:8001
RESONATE_TOKEN=your-token-here
NTFY_URL=https://ntfy.sh/your-topic
```

### Notification Backends

The example uses ntfy.sh by default, but works with any webhook:

**Slack:**
```python
url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Discord:**
```python
url = "https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

**Custom API:**
```python
url = "https://api.example.com/notifications"
```

## Testing Failure Scenarios

### Test 1: Crash During Sleep

1. Start countdown with long interval:
```bash
# 5 steps, 30 seconds each
resonate.run("test/crash", countdown, 5, 30000, url)
```

2. Wait for first notification

3. Kill the process (Ctrl+C)

4. Restart the process:
```bash
uv run python countdown.py
```

5. Observe: Countdown resumes at the correct step, no duplicates

### Test 2: Long-Running Countdown

```bash
# 24-hour countdown with hourly notifications
resonate.run("test/longrun", countdown, 24, 3600000, url)
```

Process can stop/start freely. Notifications arrive on schedule.

## Code Structure

```
countdown.py    # Countdown workflow definition
pyproject.toml  # Dependencies
```

## Key Concepts

### Durable Sleep
- `ctx.sleep(milliseconds)` suspends workflow
- Process can exit, workflow state persists
- Resonate resumes at the right time
- No polling, no cron jobs needed

### Idempotency
- Each notification uses a deterministic ID
- Replays don't duplicate notifications
- `ctx.run()` checkpoints prevent re-execution

### Resource Efficiency
- Zero CPU/memory during sleep
- Scale to zero between notifications
- Pay only for active execution time

## Production Considerations

1. **Monitoring**: Track notification delivery success
2. **Error handling**: Add retry logic for webhook failures
3. **Timeouts**: Set workflow timeout longer than total countdown
4. **Backpressure**: Limit concurrent countdown workflows
5. **Observability**: Log each notification for audit trail

## Learn More

- [Python SDK Docs](https://docs.resonatehq.io/sdk/python)
- [Durable Sleep Explained](https://docs.resonatehq.io/concepts/sleep)
- [Serverless Patterns](https://docs.resonatehq.io/patterns/serverless)

## Related Examples

- [example-countdown-ts](../example-countdown-ts) - TypeScript version
- [example-durable-sleep-py](../example-durable-sleep-py) - Basic sleep patterns
- [example-durable-sleep-ts](../example-durable-sleep-ts) - Basic sleep patterns (TypeScript)
