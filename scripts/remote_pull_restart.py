#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pull the remote backend repo and restart the backend service.

This is a small entry point for the remote part of incremental_publish.py:
- SSH into the configured server;
- sudo into a login shell;
- run git pull --ff-only under the backend root;
- restart and show status for the backend service.

Examples:
    python scripts/remote_pull_restart.py
    python scripts/remote_pull_restart.py --pull-only
    python scripts/remote_pull_restart.py --restart-only
    python scripts/remote_pull_restart.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from incremental_publish import (
    DEFAULT_REMOTE_BACKEND_ROOT,
    DEFAULT_REMOTE_HOST,
    DEFAULT_REMOTE_USER,
    DEFAULT_RESTART_COMMAND,
    PROJECT_ROOT,
    REMOTE_PASSWORD_ENV,
    PublishError,
    StageResult,
    configure_logging,
    read_remote_password_from_environment,
    remote_auth_env,
    remote_ref,
    remote_ssh_command,
    remote_sudo_input,
    run_command,
    shell_quote,
    sudo_login_shell,
)


LOGGER = logging.getLogger("remote_pull_restart")


@dataclass
class RemoteConfig:
    dry_run: bool
    keep_temp: bool
    remote_host: str
    remote_user: str
    remote_password: str
    remote_backend_root: str
    pull: bool
    restart: bool
    restart_command: str


@dataclass
class RemotePaths:
    tmp_root: Path


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_paths() -> RemotePaths:
    tmp_root = PROJECT_ROOT / ".tmp" / f"remote_pull_restart_{now_stamp()}_{os.getpid()}"
    return RemotePaths(tmp_root=tmp_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run remote backend git pull and service restart.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/remote_pull_restart.py\n"
            "  python scripts/remote_pull_restart.py --pull-only\n"
            "  python scripts/remote_pull_restart.py --restart-only\n"
            "  python scripts/remote_pull_restart.py --dry-run\n"
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the remote root command only.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary askpass files.")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    parser.add_argument("--remote-host", default=DEFAULT_REMOTE_HOST)
    parser.add_argument("--remote-user", default=DEFAULT_REMOTE_USER)
    parser.add_argument("--remote-backend-root", default=DEFAULT_REMOTE_BACKEND_ROOT)
    parser.add_argument("--restart-command", default=DEFAULT_RESTART_COMMAND)
    parser.add_argument("--pull-only", action="store_true", help="Run git pull only; do not restart.")
    parser.add_argument("--restart-only", action="store_true", help="Restart only; do not run git pull.")
    parser.add_argument(
        "--allow-passwordless",
        action="store_true",
        help=(
            "Do not require MATHNOTE_REMOTE_PASSWORD. Use only when SSH key auth "
            "and passwordless sudo are already configured."
        ),
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> RemoteConfig:
    if args.pull_only and args.restart_only:
        raise PublishError("--pull-only and --restart-only cannot be used together.")

    remote_host = str(args.remote_host).strip()
    remote_user = str(args.remote_user).strip()
    remote_backend_root = str(args.remote_backend_root).strip()
    restart_command = str(args.restart_command).strip()
    pull = not bool(args.restart_only)
    restart = not bool(args.pull_only)

    if not remote_host:
        raise PublishError("--remote-host must not be empty.")
    if not remote_user:
        raise PublishError("--remote-user must not be empty.")
    if pull and not remote_backend_root:
        raise PublishError("--remote-backend-root must not be empty when pulling.")
    if restart and not restart_command:
        raise PublishError("--restart-command must not be empty when restarting.")

    remote_password = read_remote_password_from_environment()
    if "\r" in remote_password or "\n" in remote_password:
        raise PublishError(f"${REMOTE_PASSWORD_ENV} must be a single-line value.")
    if not args.dry_run and not args.allow_passwordless and not remote_password:
        raise PublishError(
            f"Remote action requires ${REMOTE_PASSWORD_ENV}. Interactive password "
            "entry is disabled; set the current process environment variable or "
            "the Windows User/System environment variable before running."
        )

    return RemoteConfig(
        dry_run=bool(args.dry_run),
        keep_temp=bool(args.keep_temp),
        remote_host=remote_host,
        remote_user=remote_user,
        remote_password=remote_password,
        remote_backend_root=remote_backend_root,
        pull=pull,
        restart=restart,
        restart_command=restart_command,
    )


def build_root_command(config: RemoteConfig) -> str:
    steps: list[str] = []
    if config.pull:
        steps.extend(
            [
                f"cd {shell_quote(config.remote_backend_root)}",
                "git pull --ff-only",
            ]
        )
    if config.restart:
        steps.append(config.restart_command)
    return " && ".join(steps)


def command_preview(config: RemoteConfig, root_command: str) -> str:
    sudo_command = sudo_login_shell(root_command, password_stdin=bool(config.remote_password))
    ssh_command = remote_ssh_command(config, "-tt", remote_ref(config), sudo_command)
    return " ".join(ssh_command)


def run_remote(config: RemoteConfig, paths: RemotePaths) -> list[StageResult]:
    stages: list[StageResult] = []
    root_command = build_root_command(config)

    if config.dry_run:
        LOGGER.info("Dry run target | %s", remote_ref(config))
        LOGGER.info("Dry run root command | %s", root_command)
        LOGGER.info("Dry run SSH command | %s", command_preview(config, root_command))
        return stages

    paths.tmp_root.mkdir(parents=True, exist_ok=False)
    run_command(
        "remote backend git pull/restart",
        remote_ssh_command(
            config,
            "-tt",
            remote_ref(config),
            sudo_login_shell(root_command, password_stdin=bool(config.remote_password)),
        ),
        stages=stages,
        interactive=True,
        env=remote_auth_env(config, paths),
        input_text=remote_sudo_input(config),
    )
    return stages


def cleanup_temp(paths: RemotePaths, config: RemoteConfig) -> None:
    if config.dry_run or not paths.tmp_root.exists():
        return
    if config.keep_temp:
        LOGGER.info("Temp workspace kept | %s", paths.tmp_root)
        return
    shutil.rmtree(paths.tmp_root, ignore_errors=True)
    LOGGER.info("Temp workspace removed | %s", paths.tmp_root)


def main() -> int:
    args = parse_args()
    configure_logging(str(args.log_level))
    config: RemoteConfig | None = None
    paths: RemotePaths | None = None

    try:
        config = build_config(args)
        paths = create_paths()
        stages = run_remote(config, paths)
        if config.dry_run:
            LOGGER.info("Dry run complete. No remote command was executed.")
        else:
            LOGGER.info("Remote pull/restart complete | stages=%d", len(stages))
        return 0
    except PublishError as exc:
        LOGGER.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        LOGGER.error("Interrupted by user.")
        return 130
    except Exception:
        LOGGER.exception("Unexpected remote pull/restart failure")
        return 1
    finally:
        if paths is not None and config is not None:
            cleanup_temp(paths, config)


if __name__ == "__main__":
    raise SystemExit(main())
