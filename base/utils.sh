#!/bin/sh
MODPATH=${0%/*}
FRIDA_BIN="$MODPATH/bin/frida-server"
FRIDA_PORT_FILE="$MODPATH/port"
FRIDA_DEFAULT_PORT=27042
PATH="$MODPATH/bin:$PATH:/data/adb/ap/bin:/data/adb/magisk:/data/adb/ksu/bin"

# log
exec 2> $MODPATH/logs/utils.log
set -x

# Morphida morphs process names per build, so process checks are unreliable;
# detect the server through its listening port instead
get_listen_port() {
    port="$FRIDA_DEFAULT_PORT"
    if [ -f "$FRIDA_PORT_FILE" ]; then
        custom_port="$(tr -d ' \t\r\n' < "$FRIDA_PORT_FILE")"
        case "$custom_port" in
          '' | *[!0-9]*) echo "[-] Ignoring invalid port: $custom_port" >&2 ;;
          *) if [ "$custom_port" -ge 1 ] && [ "$custom_port" -le 65535 ]; then
                 port="$custom_port"
             else
                 echo "[-] Ignoring out-of-range port: $custom_port" >&2
             fi ;;
        esac
    fi
    echo "$port"
}

is_frida_running() {
    port="$(get_listen_port)"
    busybox netstat -tln 2>/dev/null | grep -q ":${port} "
}

stop_frida_server() {
    port="$(get_listen_port)"
    pids="$(busybox netstat -tlnp 2>/dev/null | grep ":${port} " | sed 's/.* \([0-9][0-9]*\)\/.*/\1/' | sort -u)"
    if [ -n "$pids" ]; then
        busybox kill -9 $pids
    else
        busybox pkill -9 'frida-server'
    fi
}

check_frida_is_up() {
    if [ -n "$1" ]; then
        timeout="$1"
    else
        timeout=4
    fi
    counter=0

    while [ $counter -lt $timeout ]; do
        if is_frida_running; then
            echo "[-] Frida-server is running... 💉😜"
            string="description=Run frida-server on boot: ✅ (active)"
            break
        else
            echo "[-] Checking Frida-server status: $counter"
            counter=$((counter + 1))
        fi
        sleep 1.5
    done

    if [ $counter -ge $timeout ]; then
        string="description=Run frida-server on boot: ❌ (failed)"
    fi

    sed -i "s/^description=.*/$string/g" $MODPATH/module.prop
}

start_frida_server() {
  if [ ! -x "$FRIDA_BIN" ]; then
    echo "[-] Frida binary not found: $FRIDA_BIN"
    string="description=Run frida-server on boot: ❌ (missing binary)"
    sed -i "s/^description=.*/$string/g" $MODPATH/module.prop
    return 1
  fi

  FRIDA_PORT="$(get_listen_port)"
  "$FRIDA_BIN" -l "127.0.0.1:$FRIDA_PORT" -D
}

wait_for_boot() {
  while true; do
    result="$(getprop sys.boot_completed)"
    if [ $? -ne 0 ]; then
      exit 1
    elif [ "$result" = "1" ]; then
      break
    fi
    sleep 3
  done
}

#EOF
