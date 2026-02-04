from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Literal
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo
import json

from ..base import Tool
from ..tool_types import ToolKind, ToolResult, ToolInvocation
from config import config


class DateTimeParams(BaseModel):
    operation: Literal["now", "format", "parse", "diff", "add"]
    timezone: str | None = None
    timestamp: str | None = None
    format_string: str | None = None
    datetime_string: str | None = None
    input_format: str | None = None
    start: str | None = None
    end: str | None = None
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class DateTimeTool(Tool):
    name: str = "datetime"
    description: str = "Get current time, format/parse datetimes, calculate differences, and add durations"
    kind: ToolKind = ToolKind.READ

    @property
    def schema(self):
        return DateTimeParams

    def _get_timezone(self, tz_str: str | None) -> ZoneInfo:
        tz_name = tz_str or config.DEFAULT_TIMEZONE
        try:
            return ZoneInfo(tz_name)
        except Exception:
            return ZoneInfo(config.DEFAULT_TIMEZONE)

    def _parse_datetime(self, dt_str: str) -> datetime:
        # Try ISO8601 first
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except Exception:
            pass

        # Try unix timestamp
        try:
            return datetime.fromtimestamp(float(dt_str), tz=timezone.utc)
        except Exception:
            pass

        raise ValueError(f"Cannot parse datetime: {dt_str}")

    def _format_output(self, dt: datetime, tz: ZoneInfo) -> str:
        dt_with_tz = dt.astimezone(tz)

        output = {
            "iso": dt_with_tz.isoformat(),
            "unix": int(dt_with_tz.timestamp()),
            "timezone": str(tz),
            "formatted": dt_with_tz.strftime("%Y-%m-%d %H:%M:%S %Z")
        }

        return json.dumps(output, indent=2)

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = DateTimeParams(**invocation.params)
        tz = self._get_timezone(params.timezone)

        try:
            if params.operation == "now":
                now = datetime.now(tz)
                return ToolResult.success_result(
                    self._format_output(now, tz),
                    metadata={"operation": "now"}
                )

            elif params.operation == "format":
                if not params.timestamp:
                    return ToolResult.error_result("timestamp required for format operation")

                dt = self._parse_datetime(params.timestamp)
                dt_with_tz = dt.astimezone(tz)

                if params.format_string:
                    formatted = dt_with_tz.strftime(params.format_string)
                    return ToolResult.success_result(
                        formatted,
                        metadata={"operation": "format", "format_string": params.format_string}
                    )
                else:
                    return ToolResult.success_result(
                        self._format_output(dt_with_tz, tz),
                        metadata={"operation": "format"}
                    )

            elif params.operation == "parse":
                if not params.datetime_string:
                    return ToolResult.error_result("datetime_string required for parse operation")

                if params.input_format:
                    try:
                        dt = datetime.strptime(params.datetime_string, params.input_format)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=tz)
                    except Exception as e:
                        return ToolResult.error_result(f"Parse error: {str(e)}")
                else:
                    dt = self._parse_datetime(params.datetime_string)

                return ToolResult.success_result(
                    self._format_output(dt, tz),
                    metadata={"operation": "parse"}
                )

            elif params.operation == "diff":
                if not params.start or not params.end:
                    return ToolResult.error_result("start and end required for diff operation")

                start_dt = self._parse_datetime(params.start)
                end_dt = self._parse_datetime(params.end)
                diff = end_dt - start_dt

                output = {
                    "total_seconds": diff.total_seconds(),
                    "days": diff.days,
                    "hours": diff.seconds // 3600,
                    "minutes": (diff.seconds % 3600) // 60,
                    "seconds": diff.seconds % 60,
                    "human_readable": str(diff)
                }

                return ToolResult.success_result(
                    json.dumps(output, indent=2),
                    metadata={"operation": "diff"}
                )

            elif params.operation == "add":
                if not params.timestamp:
                    return ToolResult.error_result("timestamp required for add operation")

                dt = self._parse_datetime(params.timestamp)
                delta = timedelta(
                    days=params.days,
                    hours=params.hours,
                    minutes=params.minutes,
                    seconds=params.seconds
                )
                new_dt = dt + delta

                return ToolResult.success_result(
                    self._format_output(new_dt, tz),
                    metadata={"operation": "add", "delta": str(delta)}
                )

            else:
                return ToolResult.error_result(f"Unknown operation: {params.operation}")

        except ValueError as e:
            return ToolResult.error_result(str(e))
        except Exception as e:
            return ToolResult.error_result(f"Unexpected error: {str(e)}")
