"""Helper methods to parse HTML returned by Cudy routers"""

import re
from datetime import datetime
from typing import Any, List
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from bs4 import BeautifulSoup


def _add_unique(data: dict[str, Any], key: str, value: Any):
    """Adds a new entry with unique ID"""

    i = 1
    unique_key = key
    while data.get(unique_key):
        i += 1
        unique_key = f"{key}{i}"
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    data[unique_key] = value


def _as_int(string: str | None) -> int | None:
    """Parses string as integer or returns None"""

    if not string:
        return None
    return int(string)


def _hex_as_int(string: str | None):
    """Parses hexadecimal string as integer or returns None"""

    if not string:
        return None
    return int(string, 16)


def _band(raw_band_info: str):
    """Gets band information"""

    if raw_band_info:
        match = re.compile(
            r".*BAND\s*(?P<band>\d+)\s*/\s*(?P<bandwidth>\d+)\s*MHz.*"
        ).match(raw_band_info)
        if match:
            return f"B{match.group('band')}"

    return None

def _seconds_duration(raw_duration: str) -> int:
    """Parses string duration and returns it as seconds"""

    if not raw_duration:
        return None
    duration_parts = raw_duration.lower().split()
    duration = relativedelta()

    for i, part in enumerate(duration_parts):
        if part.count(":") == 2:
            hours, minutes, seconds = part.split(":")
            duration += relativedelta(
                hours=_as_int(hours), minutes=_as_int(minutes), seconds=_as_int(seconds)
            )
        elif i == 0:
            continue
        elif part.startswith("year"):
            duration += relativedelta(years=_as_int(duration_parts[i - 1]))
        elif part.startswith("month"):
            duration += relativedelta(months=_as_int(duration_parts[i - 1]))
        elif part.startswith("week"):
            duration += relativedelta(weeks=_as_int(duration_parts[i - 1]))
        elif part.startswith("day"):
            duration += relativedelta(days=_as_int(duration_parts[i - 1]))

    # Get absolute duration from relative duration (considering different month lengths)
    return (datetime.now() - (datetime.now() - duration)).total_seconds()


def _speed(input_string: str) -> float:
    """Parses transfer speed as megabits per second"""

    if not input_string:
        return None
    if input_string.lower().endswith(" kbps"):
        return round(float(input_string.split(" ")[0]) / 1024, 2)
    if input_string.lower().endswith(" mbps"):
        return float(input_string.split(" ")[0])
    if input_string.lower().endswith(" gbps"):
        return float(input_string.split(" ")[0]) * 1024
    if input_string.lower().endswith(" bps"):
        return round(float(input_string.split(" ")[0]) / 1024 / 1024, 2)
    return 0


def _signal_strength(rssi: int) -> int:
    """Gets the signal strength from the RSSI value"""

    if rssi:
        if rssi > 20:
            return 4
        if rssi > 15:
            return 3
        if rssi > 10:
            return 2
        if rssi > 5:
            return 1
        return 0
    return ""


def _parse_tables(input_html: str, include_headers: bool=False) -> dict[str, Any]:
    """Parses an HTML table extracting key-value pairs"""

    data: dict[str, str] = {}
    soup = BeautifulSoup(input_html, "html.parser")
    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            cols = row.css.select("td p.visible-xs")
            if include_headers:
                cols = row.css.select("th") + cols
            row_data: list[str] = []
            for col in cols:
                stripped_text = col.text.strip()
                if stripped_text:
                    row_data.append(stripped_text)
            if len(row_data) > 1:
                _add_unique(data, row_data[0], [re.sub("[\n]", "", r) for r in row_data[1:]])
            elif len(row_data) == 1:
                _add_unique(data, row_data[0], "")

    return data


def _parse_onclick(input_html: str, cb_name: str) -> list:
    """ Retreive arguments for all buttons' onclick """

    soup = BeautifulSoup(input_html, "html.parser")
    buttons = soup.find_all('button', onclick=True)
    pattern = re.compile(r"['\"]([^'\"]+)['\"]")
    onclick_args = []
    for button in buttons:
        onclick_attr: str = button['onclick']
        if onclick_attr.startswith(cb_name):
            args = pattern.findall(onclick_attr)
            if args:
                onclick_args.append(args)
    return onclick_args


def get_sim_value(input_html: str) -> int:
    """Gets the SIM slot value out of the displayed icon"""

    soup = BeautifulSoup(input_html, "html.parser")
    sim_icon = soup.css.select_one("i.icon[class*='sim']")
    if sim_icon:
        classnames = sim_icon.attrs["class"]
        classname = next(
            iter([match for match in classnames if "sim" in match]),
            "",
        )
        if "sim1" in classname:
            return 1
        if "sim2" in classname:
            return 2
    return 0


def get_all_devices(input_html: str) -> dict[str, Any]:
    """Parses an HTML table extracting key-value pairs"""
    devices = []
    soup = BeautifulSoup(input_html, "html.parser")
    for br_element in soup.find_all("br"):
        br_element.replace_with("\n" + br_element.text)
    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            ip, mac, up_speed, down_speed, hostname = [None, None, None, None, None]
            cols = row.css.select("td div")
            for col in cols:
                div_id = col.attrs.get("id")
                content_element = col.css.select_one("p.visible-xs")
                if not div_id or not content_element:
                    continue
                content = content_element.text.strip()
                if "\n" in content:
                    if div_id.endswith("ipmac"):
                        ip, mac = [x.strip() for x in content.split("\n")]
                    if div_id.endswith("speed"):
                        up_speed, down_speed = [x.strip() for x in content.split("\n")]
                    if div_id.endswith("hostname"):
                        hostname = content.split("\n")[0].strip()
            if mac or ip:
                devices.append(
                    {
                        "hostname": hostname,
                        "ip": ip,
                        "mac": mac,
                        "up_speed": _speed(up_speed),
                        "down_speed": _speed(down_speed),
                    }
                )

    return devices


def get_devices_info(input_html: str, devices_list: str | List[str]) -> dict[str, Any]:
    """Parses devices page"""

    devices = get_all_devices(input_html)
    data = {
        "device_count": len(devices),
        "stats": {}
    }
    if devices:
        top_download_device = max(devices, key=lambda item: item.get("down_speed"))
        data['stats']["top_downloader_speed"] = top_download_device.get("down_speed")
        data['stats']["top_downloader_mac"] = top_download_device.get("mac")
        data['stats']["top_downloader_hostname"] = top_download_device.get("hostname")
        top_upload_device = max(devices, key=lambda item: item.get("up_speed"))
        data['stats']["top_uploader_speed"] = top_upload_device.get("up_speed")
        data['stats']["top_uploader_mac"] = top_upload_device.get("mac")
        data['stats']["top_uploader_hostname"] = top_upload_device.get("hostname")

        data['devices'] = []
        if isinstance(devices_list, str):
            devices_list = [x.strip() for x in (devices_list or "*").split(",")]
        data['devices'] = [device for device in devices if (devices_list[0] == "*" or device.get("hostname") in devices_list) or (device.get("mac") in devices_list)]

        data['stats']["total_down_speed"] = \
            sum(device.get("down_speed") for device in devices) or 0.0

        data['stats']["total_up_speed"] = \
            sum(device.get("up_speed") for device in devices) or 0.0

    return data


def get_modem_info(input_html: str) -> dict[str, Any]:
    """Parses modem info page"""

    raw_data = _parse_tables(input_html)
    cellid = _hex_as_int(raw_data.get("Cell ID"))
    pcc = raw_data.get("PCC") or (
        f"BAND {raw_data.get('Band')} / {raw_data.get('DL Bandwidth')}"
        if (raw_data.get("Band") and raw_data.get("DL Bandwidth"))
        else None
    )
    scc1 = raw_data.get("SCC")
    scc2 = raw_data.get("SCC2")
    scc3 = raw_data.get("SCC3")
    scc4 = raw_data.get("SCC4")
    data: dict[str, dict[str, Any]] = {
        "network": {
            "name": (raw_data.get("Network Type") or "").replace(" ...", ""),
            "attributes": {"mcc": raw_data.get("MCC"), "mnc": raw_data.get("MNC")},
        },
        "connected_time": _seconds_duration(raw_data.get("Connected Time")),
        "signal": _signal_strength(_as_int(raw_data.get("RSSI"))),
        "rssi": _as_int(raw_data.get("RSSI")),
        "rsrp": _as_int(raw_data.get("RSRP")),
        "rsrq": _as_int(raw_data.get("RSRQ")),
        "sinr": _as_int(raw_data.get("SINR")),
        "sim": get_sim_value(input_html),
        "band": filter(
                    None,
                    (_band(pcc), _band(scc1), _band(scc2), _band(scc3), _band(scc4)),
                ),
        "cell": {
            "cell_id_hex": raw_data.get("Cell ID"),
            "cell_id": cellid,
            "enb": cellid // 256 if cellid else None,
            "sector": cellid % 256 if cellid else None,
            "pc_id": _as_int(raw_data.get("PCID")),
        },
    }
    return data

def get_login_info(input_html: str) -> dict[str, Any]:
    """ parse the login screen to extract inpt fields """

    data: dict[str, str] = {}
    soup = BeautifulSoup(input_html, "html.parser")
    form_inputs = soup.find_all("input")
    for form_input in form_inputs:
        if name := form_input.attrs.get('name', form_input.attrs.get('id')):
            data[name] = form_input.attrs.get('value', "")
    return data


def get_sms_summary(input_html: str) -> dict[str, Any]:
    """Parses SMS summary"""

    raw_data = _parse_tables(input_html, include_headers=True)

    data: dict[str, dict[str, Any]] = {
        'new_messages_count': _as_int(raw_data.get('New Message')),
        'inbox_count': _as_int(raw_data.get('Inbox')),
        'outbox_count': _as_int(raw_data.get('Outbox'))
    }

    return data


def get_sms_list(input_html: str) -> dict[str, Any]:
    """Parses SMS list table"""

    sms_list = _parse_tables(input_html)
    onclick_args = _parse_onclick(input_html, "cbi_show_modal")
    readsms_args = [arg[1] for arg in onclick_args if "readsms" in arg[0]]
    sms_cfgs = (re.search(r"cfg=([a-z0-9]+)", readsms).group(1) for readsms in readsms_args)

    sms_messages = []
    for index, values in sms_list.items():
        sms_messages.append({
            'index': _as_int(index),
            'phone_number': values[0],
            'text': values[1],
            'timestamp': parse(values[2]),
            'cfg': next(sms_cfgs)
        })

    return sms_messages


def read_sms(input_html) -> dict[str, Any]:
    """ read sms from the router """

    soup = BeautifulSoup(input_html, "html.parser")
    phone_input = soup.find("input", id="cbid.smsread.1.phone")
    text_textarea = soup.find("textarea", id="cbid.smsread.1.text")

    return {
        'phone_number': phone_input['value'] if phone_input else "",
        'text': text_textarea.contents[0] if text_textarea else ""
    }
