# Logs Directory

## Purpose
System logs and crash reports for debugging and monitoring.

## Directory Structure

### `crash/` - Crash Reports
Python stack traces and error logs from application crashes.
- Auto-generated when exceptions occur
- Includes timestamp, error type, and stack trace
- Used for debugging production issues

## Usage

Logs are automatically created by the application when:
- Unhandled exceptions occur
- Critical errors are encountered
- System crashes or failures happen

## File Format

Crash logs are named:
```
crash-YYYYMMDD-HHMMSS.txt
```

Example: `crash-20251125-001828.txt`

## Monitoring

Regularly review logs to:
- Identify recurring errors
- Debug production issues
- Monitor system stability
- Track error patterns

## Retention

Old logs can be archived or deleted after analysis. Consider:
- Keep logs for 30-90 days
- Archive important crash reports
- Delete resolved issues' logs
