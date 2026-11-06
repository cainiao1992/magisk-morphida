# Troubleshooting

## Try first
- Ensure `adb devices` shows your device
- Ensure `adb shell` opens a working shell on your device
- Try running the Morphida server [through an ADB shell](https://frida.re/docs/android/)
- Ensure Magisk is at a STABLE version and up-to-date
- Ensure MagiskHide is disabled
- Ensure you are on an AOSP-based ROM
- Ensure your client version matches the server (`frida --version` == server version prefix)

## Not solved?
Please open an issue and post detailed information about your device (including logs!)
