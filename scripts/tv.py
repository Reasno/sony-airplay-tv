#!/usr/bin/env python3
"""Install and manage Sony AirPlay over Android Debug Bridge."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

PACKAGE = "com.guxi.sonyairplay"
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", help="ADB device serial, e.g. 192.168.1.20:5555")
    commands = parser.add_subparsers(dest="command", required=True)
    connect = commands.add_parser("connect")
    connect.add_argument("address")
    install = commands.add_parser("install")
    built_apk = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
    delivered_apk = ROOT / "dist/sony-airplay-tv-0.1.0-debug.apk"
    install.add_argument("--apk", type=Path, default=built_apk if built_apk.is_file() else delivered_apk)
    for name in ("start", "settings", "status", "logs"):
        commands.add_parser(name)
    setting = commands.add_parser("set")
    setting.add_argument("key")
    setting.add_argument("value")
    args = parser.parse_args()
    if not shutil.which("adb"):
        parser.error("adb is required (Android SDK platform-tools)")

    def adb(*parts):
        prefix = ["adb"] + (["-s", args.serial] if args.serial else [])
        subprocess.run(prefix + list(parts), check=True)

    def launch(settings=False):
        adb("shell", "am", "start", "-n", f"{PACKAGE}/.MainActivity",
            "--ez", "show_settings", str(settings).lower())

    def set_pref(key, value):
        # am receives a shell command on the device; quote arbitrary values there.
        import shlex
        parts = ["am", "broadcast", "-n", f"{PACKAGE}/.SettingsReceiver",
                 "-a", f"{PACKAGE}.SET_SETTING", "--es", "key", key,
                 "--es", "value", value]
        adb("shell", shlex.join(parts))

    if args.command == "connect":
        adb("connect", args.address)
    elif args.command == "install":
        if not args.apk.is_file():
            parser.error(f"APK does not exist: {args.apk}")
        adb("install", "-r", str(args.apk))
        adb("shell", "appops", "set", PACKAGE, "SYSTEM_ALERT_WINDOW", "allow")
        for key in ("headless", "auto_start", "boot_auto_start", "run_in_background",
                    "launch_on_connect", "advertise_video", "advertise_mirroring"):
            set_pref(key, "true")
        launch()
    elif args.command == "start":
        launch()
    elif args.command == "settings":
        launch(settings=True)
    elif args.command == "set":
        set_pref(args.key, args.value)
    elif args.command == "status":
        adb("shell", "getprop", "ro.product.model")
        adb("shell", "getprop", "ro.build.version.release")
        adb("shell", "getprop", "ro.product.cpu.abilist")
        adb("shell", "dumpsys", "activity", "services", PACKAGE)
        adb("shell", "am", "broadcast", "-n", f"{PACKAGE}/.SettingsReceiver",
            "-a", f"{PACKAGE}.LIST_SETTINGS")
    elif args.command == "logs":
        adb("logcat", "-v", "time", "AirPlayService:I", "AirPlayNative:I", "*:S")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
