# MagiskMorphida

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/cainiao1992/magisk-morphida/main.yml?branch=master)
![GitHub repo size](https://img.shields.io/github/repo-size/cainiao1992/magisk-morphida)
![GitHub downloads](https://img.shields.io/github/downloads/cainiao1992/magisk-morphida/total)

> [Morphida](https://github.com/1013503897/Morphida) is a rebuilt, polymorphic anti-detection `frida-server` for Android arm64 — same client, same version number, different binary

> [MagiskMorphida](README.md) lets you run the Morphida frida-server on boot with multiple root solutions

## Supported root solutions

[Magisk](https://github.com/topjohnwu/Magisk), [KernelSU](https://github.com/tiann/KernelSU) and [APatch](https://github.com/bmax121/APatch)

## Supported architecture

`arm64` (Morphida only publishes arm64 builds)

## Instructions

Install `MagiskMorphida.zip` from [the releases](https://github.com/cainiao1992/magisk-morphida/releases)

> :information_source: Do not use the Magisk modules repository, it is obsolete and no longer receives updates

## Custom port

The server listens on `127.0.0.1:27042` by default. To change it, write the port to `/data/adb/modules/magisk-morphida/port` and reboot

```bash
echo 41337 > /data/adb/modules/magisk-morphida/port
```

## How fast are server updates?

Instant! This module is hooked up to the official Morphida build process

## Client

Keep using the official Frida client; client and server versions must match (`frida --version` == server version prefix)

```bash
pip install frida==<version>
frida-ps -U
```

## Issues?

Check out the [troubleshooting guide](TROUBLESHOOTING.md)

## Building yourself

```bash
uv sync
uv run python3 main.py
```

- Release ZIP will be under `/build`
- server downloads will be under `/downloads`
