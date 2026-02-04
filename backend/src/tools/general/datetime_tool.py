from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from typing import Literal

import tzdata 
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

from config import config

from ..base import Tool
from ..tool_types import ToolInvocation, ToolKind, ToolResult


class DateTimeParams(BaseModel):
    operation: Literal["now", "format", "parse", "diff", "add"] = Field(
        description="Operation to perform"
    )
    timezone: str | None = Field(
        default=None,
        description="IANA timezone (e.g. America/New_York)"
    )
    timestamp: str | None = Field(
        default=None,
        description="ISO8601 or unix timestamp (for format/add, defaults to now for add)"
    )
    format_string: str | None = Field(
        default=None,
        description="strftime format string"
    )
    datetime_string: str | None = Field(
        default=None,
        description="String to parse (for parse)"
    )
    input_format: str | None = Field(
        default=None,
        description="strptime format for parsing"
    )

    # diff calculation fields
    start: str | None = Field(
        default=None,
        description="Start timestamp (for diff)"
    )
    end: str | None = Field(
        default=None,
        description="End timestamp (for diff)"
    )
    days: int = Field(
        default=0,
        description="Days to add"
    )
    hours: int = Field(
        default=0,
        description="Hours to add"
    )
    minutes: int = Field(
        default=0,
        description="Minutes to add"
    )
    seconds: int = Field(
        default=0,
        description="Seconds to add"
    )

class DateTimeTool(Tool):
    name: str = "datetime"
    description: str = "Get current time, format/parse datetimes, calculate differences, and add durations"
    kind: ToolKind = ToolKind.READ

    @property
    def schema(self):
        return DateTimeParams

    def _get_timezone(self, tz_str: str | None) -> ZoneInfo:
        try:
            return ZoneInfo(tz_str or config.DEFAULT_TIMEZONE)
        except Exception:
            return ZoneInfo(config.DEFAULT_TIMEZONE)

    def _parse_datetime(self, dt_str: str) -> datetime:
        # ISO8601
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except Exception:
            pass
        # Unix timestamp
        try:
            return datetime.fromtimestamp(float(dt_str), tz=timezone.utc)
        except Exception:
            pass
        raise ValueError(f"Cannot parse datetime: {dt_str}")

    def _format_output(self, dt: datetime, tz: ZoneInfo) -> str:
        dt_tz = dt.astimezone(tz)
        return json.dumps({
            "iso": dt_tz.isoformat(),
            "unix": int(dt_tz.timestamp()),
            "timezone": str(tz),
            "formatted": dt_tz.strftime("%Y-%m-%d %H:%M:%S %Z")
        }, indent=2)

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = DateTimeParams(**invocation.params)
        tz = self._get_timezone(params.timezone)

        try:
            match params.operation:
                case "now":
                    return ToolResult.success_result(
                        self._format_output(datetime.now(tz), tz),
                        metadata={"operation": "now"}
                    )

                case "format":
                    if not params.timestamp:
                        return ToolResult.error_result("timestamp required for format operation")
                    dt = self._parse_datetime(params.timestamp).astimezone(tz)
                    if params.format_string:
                        return ToolResult.success_result(
                            dt.strftime(params.format_string),
                            metadata={"operation": "format", "format_string": params.format_string}
                        )
                    return ToolResult.success_result(
                        self._format_output(dt, tz),
                        metadata={"operation": "format"}
                    )

                case "parse":
                    if not params.datetime_string:
                        return ToolResult.error_result("datetime_string required for parse operation")
                    if params.input_format:
                        try:
                            dt = datetime.strptime(params.datetime_string, params.input_format)
                            dt = dt.replace(tzinfo=tz) if dt.tzinfo is None else dt
                        except Exception as e:
                            return ToolResult.error_result(f"Parse error: {e}")
                    else:
                        dt = self._parse_datetime(params.datetime_string)
                    return ToolResult.success_result(
                        self._format_output(dt, tz),
                        metadata={"operation": "parse"}
                    )

                case "diff":
                    if not params.start or not params.end:
                        return ToolResult.error_result("start and end required for diff operation")
                    start_dt = self._parse_datetime(params.start)
                    end_dt = self._parse_datetime(params.end)
                    total_secs = (end_dt - start_dt).total_seconds()
                    
                    # Compute breakdown from total seconds (handles negative)
                    abs_secs = abs(int(total_secs))
                    days, remainder = divmod(abs_secs, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, secs = divmod(remainder, 60)
                    sign = -1 if total_secs < 0 else 1
                    
                    return ToolResult.success_result(
                        json.dumps({
                            "total_seconds": total_secs,
                            "days": sign * days,
                            "hours": hours,
                            "minutes": minutes,
                            "seconds": secs,
                            "human_readable": f"{'-' if sign < 0 else ''}{days} days, {hours}:{minutes:02d}:{secs:02d}"
                        }, indent=2),
                        metadata={"operation": "diff"}
                    )

                case "add":
                    if params.timestamp:
                        dt = self._parse_datetime(params.timestamp)
                    else:
                        dt = datetime.now(tz)  # default to now
                    delta = timedelta(
                        days=params.days, hours=params.hours,
                        minutes=params.minutes, seconds=params.seconds
                    )
                    return ToolResult.success_result(
                        self._format_output(dt + delta, tz),
                        metadata={"operation": "add", "delta": str(delta)}
                    )

        except ValueError as e:
            return ToolResult.error_result(str(e))
        except Exception as e:
            return ToolResult.error_result(f"Unexpected error: {e}")
