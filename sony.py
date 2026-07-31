import requests
import json
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class SonyLIV:
    BASE_URL = "https://apiv2.sonyliv.com"
    APP_VERSION = "3.3.58"

    # Official logo data from Sony Pictures Networks
    OFFICIAL_LOGOS = {
        "Sony Entertainment Television": "https://www.sonypicturesnetworks.com/images/logos/SET LOGO.png",
        "Sony Entertainment Television HD": "https://www.sonypicturesnetworks.com/images/logos/SET-LOGO-HD.png",
        "Sony PIX": "https://www.sonypicturesnetworks.com/images/logos/PIX SD.png",
        "Sony PIX HD": "https://www.sonypicturesnetworks.com/images/logos/PIX HD_WHITE.png",
        "Sony BBC Earth": "https://www.sonypicturesnetworks.com/images/logos/SBBCE_LOGO_NEW_AI_SD.png",
        "Sony BBC Earth HD": "https://www.sonypicturesnetworks.com/images/logos/SBBCE_LOGO_NEW_PNG.png",
        "Sony PAL": "https://www.sonypicturesnetworks.com/images/logos/SONY PAL.png",
        "Sony AATH": "https://www.sonypicturesnetworks.com/images/logos/SONY AATH.png",
        "Sony SAB": "https://www.sonypicturesnetworks.com/images/logos/SONY SAB SD.png",
        "Sony SAB HD": "https://www.sonypicturesnetworks.com/images/logos/SONY SAB HD_WHITE.png",
        "Sony YAY!": "https://www.sonypicturesnetworks.com/images/logos/SONY YAY.png",
        "Sony Marathi": "https://www.sonypicturesnetworks.com/images/logos/Sony_MARATHI.png",
        "Sony MAX": "https://www.sonypicturesnetworks.com/images/logos/Sony_MAX.png",
        "Sony MAX HD": "https://www.sonypicturesnetworks.com/images/logos/Sony_MAX-HD_WHITE.png",
        "Sony MAX1": "https://www.sonypicturesnetworks.com/images/logos/Sony_MAX1.png",
        "Sony MAX2": "https://www.sonypicturesnetworks.com/images/logos/Sony_MAX2.png",
        "Sony WAH": "https://www.sonypicturesnetworks.com/images/logos/Sony_WAH.png",
        "Sony Sports Network": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsNetwork_Logo_CLR.png",
        "Sony Sports Ten1": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen1_SD_Logo_CLR.png",
        "Sony Sports Ten1 HD": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen1_HD_Logo_CLR.png",
        "Sony Sports Ten2": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen2_SD_Logo_CLR.png",
        "Sony Sports Ten2 HD": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen2_HD_Logo_CLR.png",
        "Sony Sports Ten3 Hindi": "https://www.sonypicturesnetworks.com/images/logos/Sony_Sports_Ten_3_Hindi.png",
        "Sony Sports Ten3 Hindi HD": "https://www.sonypicturesnetworks.com/images/logos/Sony_Sports_Ten_3_Hindi_HD.png",
        "Sony Sports Ten4 Tamil": "https://www.sonypicturesnetworks.com/images/logos/Sony_Sports_Ten_4_Tamil.png",
        "Sony Sports Ten4 Telugu": "https://www.sonypicturesnetworks.com/images/logos/Sony_Sports_Ten_4_Telugu.png",
        "Sony Sports Ten5": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen5_SD_Logo_CLR.png",
        "Sony Sports Ten5 HD": "https://www.sonypicturesnetworks.com/images/logos/SONY_SportsTen5_HD_Logo_CLR.png",
        "Sony LIV": "https://www.sonypicturesnetworks.com/images/logos/Sony_LIV.png",
    }

    # Map our channel names to the official logo keys
    LOGO_MAP = {
        "SET HD": "Sony Entertainment Television HD",
        "Sony SAB HD": "Sony SAB HD",
        "Sony Marathi": "Sony Marathi",
        "Sony Pal": "Sony PAL",
        "Sony Aath": "Sony AATH",
        "Sony Yay": "Sony YAY!",
        "Sony MAX HD": "Sony MAX HD",
        "Sony MAX": "Sony MAX",
        "Sony MAX 2": "Sony MAX2",
        "Sony WAH": "Sony WAH",
        "Sony PIX HD": "Sony PIX HD",
        "Sony Sports Ten 1 HD": "Sony Sports Ten1 HD",
        "Sony Sports Ten 1": "Sony Sports Ten1",
        "Sony Sports Ten 2": "Sony Sports Ten2",
        "Sony Sports Ten 3": "Sony Sports Ten3 Hindi",   # We only have Hindi SD/HD; we'll use Hindi SD
        "Sony Sports Ten 4": "Sony Sports Ten4 Tamil",   # Choose Tamil as default
        "Sony Sports Ten 5": "Sony Sports Ten5",
        "Sony Sports Ten 2 HD": "Sony Sports Ten2 HD",
        "Sony Sports Ten 3 HD": "Sony Sports Ten3 Hindi HD",
        "Sony Sports Ten 4 HD": "Sony Sports Ten4 Tamil",  # No HD logo, fallback to Tamil
        # Note: "Sony Sports Ten 4 HD" appears also in CHANNELS; we map to Tamil
    }

    # Static channel data (base URLs without query string)
    CHANNELS = [
        {"name": "SET HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011671/SETHD/master.m3u8"},
        {"name": "Sony SAB HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011749/SABHD/master.m3u8"},
        {"name": "Sony Marathi", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011740/SonyMarathi/master.m3u8"},
        {"name": "Sony Pal", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011741/SonyPalSD/master.m3u8"},
        {"name": "Sony Aath", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011641/SonyAathSD/master.m3u8"},
        {"name": "Sony Yay", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011746/SonyYaySD/master.m3u8"},
        {"name": "Sony MAX HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011670/SonyMaxhd/master.m3u8"},
        {"name": "Sony MAX", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011745/SonyMaxSD/master.m3u8"},
        {"name": "Sony MAX 2", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011908/MAX2/master.m3u8"},
        {"name": "Sony WAH", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011906/SonyWah/master.m3u8"},
        {"name": "Sony PIX HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011748/PIXHD/master.m3u8"},
        {"name": "Sony Sports Ten 1 HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011747/TEN1HD/master.m3u8"},
        {"name": "Sony Sports Ten 1", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2011739/TEN1SD/master.m3u8"},
        {"name": "Sony Sports Ten 2", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020590/TEN2SD/master.m3u8"},
        {"name": "Sony Sports Ten 3", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020592/TEN3SD/master.m3u8"},
        {"name": "Sony Sports Ten 4", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020437/ten4sd/master.m3u8"},
        {"name": "Sony Sports Ten 5", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020594/SONYSIXSD/master.m3u8"},
        {"name": "Sony Sports Ten 2 HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020434/TEN2HD/master.m3u8"},
        {"name": "Sony Sports Ten 3 HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020591/TEN3HD/master.m3u8"},
        {"name": "Sony Sports Ten 4 HD", "logo": "", "base_url": "https://dishmt.slivcdn.com/hls/live/2020589/ten4hd/master.m3u8"},
    ]

    # Fill in the logos using the map
    for ch in CHANNELS:
        key = ch["name"]
        if key in LOGO_MAP:
            logo_key = LOGO_MAP[key]
            ch["logo"] = OFFICIAL_LOGOS.get(logo_key, "")
        else:
            ch["logo"] = ""  # fallback to empty

    _cookie_cache = None
    _cookie_exp = 0

    @classmethod
    def _get(cls, url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def token(cls) -> str:
        url = f"{cls.BASE_URL}/AGL/1.4/A/ENG/WEB/ALL/GETTOKEN"
        data = cls._get(url)
        result = data.get("resultObj")
        if isinstance(result, dict):
            token = result.get("token") or result.get("securityToken")
        elif isinstance(result, str):
            token = result
        else:
            token = None
        if not token:
            raise ValueError("Token not found in response")
        return token

    @classmethod
    def headers(cls) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-via-device": "true",
            "security_token": cls.token(),
            "app_version": cls.APP_VERSION,
        }

    @classmethod
    def get_cookie_and_expiry(cls) -> Tuple[Optional[str], Optional[int]]:
        now = time.time()
        if cls._cookie_cache and cls._cookie_exp > now + 10:
            return cls._cookie_cache, cls._cookie_exp

        sample_id = "1090491205"
        try:
            full_url = cls.video_url(sample_id)
        except Exception:
            return None, None

        if "?" in full_url:
            query = full_url.split("?", 1)[1]
            exp_match = re.search(r"exp=(\d+)", query)
            if exp_match:
                exp = int(exp_match.group(1))
                cls._cookie_cache = query
                cls._cookie_exp = exp
                return query, exp
        return None, None

    @classmethod
    def video_url(cls, content_id: str) -> str:
        url = f"{cls.BASE_URL}/AGL/1.5/A/ENG/WEB/IN/CONTENT/VIDEOURL/VOD/{content_id}/freepreview"
        data = cls._get(url, headers=cls.headers())
        result = data.get("resultObj", {})
        video_url = result.get("videoURL")
        if not video_url:
            raise ValueError(f"No videoURL for content {content_id}")
        return video_url

    @classmethod
    def _get_group_title(cls, name: str) -> str:
        name_lower = name.lower()
        if "sports" in name_lower or "ten" in name_lower or "six" in name_lower:
            return "Sports"
        elif "max" in name_lower or "wah" in name_lower or "pix" in name_lower:
            return "Movies"
        elif "yay" in name_lower:
            return "Kids"
        else:
            return "Entertainment"

    @classmethod
    def generate_playlist(cls) -> Tuple[str, str, int, Dict[str, int]]:
        cookie, exp = cls.get_cookie_and_expiry()
        if not cookie:
            raise RuntimeError("Failed to obtain cookie for M3U8 URLs")

        exp_time = datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M:%S") if exp else "Unknown"
        total = len(cls.CHANNELS)

        lines = ["#EXTM3U"]
        lines.append(f"# TOTAL Channels: {total}")
        lines.append(f"# cookie_time: {exp_time}")
        lines.append("")

        group_counts = {}
        for ch in cls.CHANNELS:
            name = ch["name"]
            logo = ch.get("logo", "")
            base = ch["base_url"]
            group = cls._get_group_title(name)
            group_counts[group] = group_counts.get(group, 0) + 1
            full_url = f"{base}?{cookie}"
            lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}", {name}')
            lines.append(full_url)

        return "\n".join(lines), exp_time, total, group_counts

    @classmethod
    def show_summary(cls, exp_time: str, total: int, group_counts: Dict[str, int]):
        print("=" * 60)
        print(f"✅ Success – Cookie retrieved and playlist generated.")
        print(f"   Total channels: {total}")
        print(f"   Total groups: {len(group_counts)}")
        for grp, count in group_counts.items():
            print(f"      - {grp}: {count} channels")
        print(f"   Cookie expiry: {exp_time}")
        print("-" * 60)
        print(f"{'#':<4} {'Channel Name':<30} {'Group':<15} {'Status'}")
        print("-" * 60)
        for idx, ch in enumerate(cls.CHANNELS, 1):
            group = cls._get_group_title(ch["name"])
            status = "✅" if exp_time != "Unknown" else "❌"
            print(f"{idx:<4} {ch['name']:<30} {group:<15} {status}")
        print("=" * 60)
        print(f"Playlist saved as: sony_liv.m3u")

# IPTV hooks (unchanged)
def iptv_sonyliv(id_str: str) -> bool:
    if id_str.startswith("sonyliv-"):
        content_id = id_str.replace("sonyliv-", "")
        try:
            url = SonyLIV.video_url(content_id)
            print(f"Playing HLS (URL hidden).")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    return False

def iptv_sonyliv2(id_str: str) -> bool:
    if "dishmt.slivcdn.com/hls/live/" in id_str:
        cookie, _ = SonyLIV.get_cookie_and_expiry()
        if cookie:
            final_url = id_str.split("?")[0] + "?" + cookie
            print(f"Playing with refreshed cookie (URL hidden).")
            return True
        else:
            print("Could not retrieve cookie")
            return False
    return False

if __name__ == "__main__":
    try:
        playlist, exp_time, total, group_counts = SonyLIV.generate_playlist()
        with open("sony_liv.m3u", "w", encoding="utf-8") as f:
            f.write(playlist)
        SonyLIV.show_summary(exp_time, total, group_counts)
    except Exception as e:
        print(f"❌ Error: {e}")
