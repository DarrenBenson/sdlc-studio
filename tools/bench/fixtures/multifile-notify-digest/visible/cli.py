"""Command-line console for the notification service.

``main`` operates on the service instance passed in (or a fresh
in-memory one), so the CLI doubles as the embedding seam used by the
tests. Only this boundary may default ``now`` to the wall clock
(SPEC R10).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from routing import NotificationService


def _parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    return datetime.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="notify", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-user", help="register a user")
    p.add_argument("user_id")
    p.add_argument("--unsubscribed", action="store_true")
    p.add_argument("--utc-offset", type=int, default=0)

    p = sub.add_parser("notify", help="create and route a notification")
    p.add_argument("user_id")
    p.add_argument("body")
    p.add_argument("--urgent", action="store_true")
    p.add_argument("--mandatory", action="store_true")
    p.add_argument("--now", help="ISO timestamp (UTC); defaults to wall clock")

    p = sub.add_parser("release-deferred", help="re-attempt quiet-hours deferrals")
    p.add_argument("--now")

    p = sub.add_parser("audit", help="print the audit log")
    p.add_argument("user_id", nargs="?")

    return parser


def main(argv: list[str] | None = None, service: NotificationService | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = service or NotificationService()

    if args.command == "add-user":
        service.add_user(
            args.user_id,
            subscribed=not args.unsubscribed,
            utc_offset_hours=args.utc_offset,
        )
        print(f"added {args.user_id}")
    elif args.command == "notify":
        delivery = service.notify(
            args.user_id,
            args.body,
            urgent=args.urgent,
            mandatory=args.mandatory,
            now=_parse_now(args.now),
        )
        print("delivered" if delivery else "not delivered")
    elif args.command == "release-deferred":
        made = service.release_deferred(now=_parse_now(args.now))
        print(f"released {len(made)}")
    elif args.command == "audit":
        entries = (
            service.audit.for_user(args.user_id)
            if args.user_id
            else service.audit.entries
        )
        for entry in entries:
            print(
                f"{entry.at.isoformat()} {entry.user_id} "
                f"{entry.reason} {entry.notification_ids}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
