import subprocess
import re
import time
from collections import defaultdict
import yeelight

DEVICES_MACS = {
    "XXXXX": "Omer's iPhone",
    "XXXXX": "Omer's iPhone",
}

DEVICE_LAST_SEEN_DICT = defaultdict(lambda: {"time": 0, "connected": False})
LAST_SEEN_TIME_THRESHOLD_MINTURES = 20


def get_ip_by_mac(mac_to_search: str) -> str:
    ans = subprocess.check_output("arp -a", shell=True).decode().upper()

    mac_ip_dict = {}

    for line in ans.splitlines():
        ip, mac = line.split(" ")[1], line.split(" ")[3]
        # remove brackets from ip
        ip = re.sub("\(|\)", "", ip)
        mac_ip_dict[mac] = ip

    return mac_ip_dict[mac_to_search] if mac_to_search in mac_ip_dict else ""


def ping_ip(ip: str):
    try:
        ans = subprocess.check_output(
            "ping -c 1 {}".format(ip), shell=True).decode()
        if "bytes from" in ans:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


def get_yeelight_bulbs():
    bulbs = []
    for b in yeelight.discover_bulbs():
        bulbs.append(yeelight.Bulb(b["ip"]))

    return bulbs


def turn_off_lights():
    for bulb in get_yeelight_bulbs():
        bulb.turn_off()


def main():
    print("Starting...")
    while True:
        for mac in DEVICES_MACS:
            ip = get_ip_by_mac(mac)

            if ip and ping_ip(ip):
                DEVICE_LAST_SEEN_DICT[mac]["time"] = time.time()
                if not DEVICE_LAST_SEEN_DICT[mac]["connected"]:
                    print("{} is Connected".format(DEVICES_MACS[mac]))
                    DEVICE_LAST_SEEN_DICT[mac]["connected"] = True

            else:
                if mac in DEVICE_LAST_SEEN_DICT:
                    print("{} was last seen at {}".format(
                        DEVICES_MACS[mac], time.ctime(DEVICE_LAST_SEEN_DICT[mac]["time"])))
                    DEVICE_LAST_SEEN_DICT[mac]["connected"] = False
                    if time.time() - DEVICE_LAST_SEEN_DICT[mac]["time"] > 60 * LAST_SEEN_TIME_THRESHOLD_MINTURES:
                        turn_off_lights()
        time.sleep(1)


if __name__ == "__main__":
    main()
