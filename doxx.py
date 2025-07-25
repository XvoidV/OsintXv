import os
import sys
import time
import json
import re
import random
import string
import webbrowser
import requests
import time
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from getpass import getpass

from googlesearch import search
from lxml.html import fromstring
import textwrap

try:
    import requests
    from bs4 import BeautifulSoup
    import phonenumbers as pnumb
    from phonenumbers import parse, geocoder, carrier, timezone
    from colorama import Fore, Style, init
    import whois
    import dns.resolver
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError:
    print(f"{Fore.RED}Beberapa pustaka yang diperlukan belum terinstal.")
    print(
        f"Silakan instal dengan: pip install requests beautifulsoup4 phonenumbers colorama dnspython python-whois google-search-results lxml{Style.RESET_ALL}"
    )
    sys.exit(1)

init(autoreset=True)

TIKTOK_API_KEY = "Xvoid"
IPQUALITYSCORE_API_KEY = "lPnx5AhAUv4jgIFDXquYpe8CVBjmaTii"

DATA_NIK_PATH = "data/data.json"
SITES_DATA_PATH = "data/sites_data.json"
UA_FILE = 'tools/ua.txt'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
]

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
DARK_GRAY = Fore.WHITE + Style.DIM
WHITE = Fore.WHITE
RESET_ALL = Style.RESET_ALL

BG_BLUE_SIMULATED = f"{Fore.BLUE}{Style.BRIGHT}"

SPACE_PREFIX = "         "
LINES_SEPARATOR = SPACE_PREFIX + "-" * 44

HEADERS = {
    "User-Agent":
    "Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54"
}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_animation(message, duration=2):
    chars = "/-\\|"
    for i in range(duration * 10):
        sys.stdout.write(
            f"\r{Fore.YELLOW}{message} {chars[i % len(chars)]}{Style.RESET_ALL}"
        )
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")
    sys.stdout.flush()


def print_banner():
    clear_screen()
    ascii_dox = f"""{Fore.RED}{Style.BRIGHT}
██████╗  ██████╗ ██╗  ██╗
██╔══██╗██╔═══██╗╚██╗██╔╝
██║  ██║██║   ██║ ╚███╔╝ 
██║  ██║██║   ██║ ██╔██╗ 
██████╔╝╚██████╔╝██╔╝ ██╗
╚═════╝  ╚═════╝ ╚═╝  ╚═╝
{Style.RESET_ALL}"""

    print(ascii_dox)
    print(
        f"{Fore.RED}{Style.BRIGHT}==========================================")
    print(f"|           OSINT TOOL BY XVOID          |")
    print(f"==========================================")
    print(f"=========================================={Style.RESET_ALL}\n")


def check_phone_info(number):
    print(f"\n{Fore.YELLOW}--- Informasi Nomor Telepon ---{Style.RESET_ALL}")
    loading_animation("Menganalisis nomor...", duration=1)

    try:
        parsing = parse(number)

        if not pnumb.is_valid_number(parsing) or not pnumb.is_possible_number(
                parsing):
            print(
                f"{Fore.RED}Nomor tidak valid atau tidak mungkin. Silakan coba lagi.{Style.RESET_ALL}"
            )
            return

        loc = geocoder.description_for_number(parsing, "id")
        isp = carrier.name_for_number(parsing, "id")
        tz = timezone.time_zones_for_number(parsing)

        if not loc and not isp and not tz:
            print(
                f"{Fore.YELLOW}Informasi dasar tidak dapat ditemukan untuk nomor ini.{Style.RESET_ALL}"
            )
            return

        data = {
            "International Format":
            pnumb.format_number(parsing,
                                pnumb.PhoneNumberFormat.INTERNATIONAL),
            "National Format":
            pnumb.national_significant_number(parsing),
            "Valid Number":
            pnumb.is_valid_number(parsing),
            "Can Be Internationally Dialled":
            pnumb.can_be_internationally_dialled(parsing),
            "Location":
            loc if loc else "Tidak diketahui",
            "Region Code For Number":
            pnumb.region_code_for_number(parsing),
            "Number Type":
            pnumb.number_type(parsing),
            "Is Carrier Specific":
            pnumb.is_carrier_specific(parsing),
            "ISP":
            isp if isp else "Tidak diketahui",
            "Time Zone":
            ", ".join(tz) if tz else "Tidak diketahui",
            "WhatsApp Link":
            f"https://wa.me/{pnumb.format_number(parsing, pnumb.PhoneNumberFormat.E164)}",
            "Is Number Geographical":
            pnumb.is_number_geographical(parsing)
        }

        for key, value in data.items():
            print(
                f"{Fore.CYAN}{key.ljust(30)}{Style.RESET_ALL}: {Fore.WHITE}{value}"
            )
            time.sleep(0.05)

    except Exception as e:
        print(f"{Fore.RED}Error saat memproses nomor: {e}{Style.RESET_ALL}")


def run_phone_lookup_menu():
    number = input(
        f"{Fore.YELLOW}Masukkan nomor telepon (contoh: 6281234567890 atau +6281234567890): {Style.RESET_ALL}"
    )
    number = number.strip().replace(" ", "")

    if not number:
        print(f"{Fore.RED}Nomor tidak boleh kosong!{Style.RESET_ALL}")
        time.sleep(1)
        return

    try:
        if not number.startswith('+'):
            parsed_number = parse(number, "ID")
            if pnumb.is_valid_number(parsed_number):
                number_e164 = pnumb.format_number(parsed_number,
                                                  pnumb.PhoneNumberFormat.E164)
            else:
                if not number.startswith('62'):
                    temp_number = '62' + number
                    parsed_number = parse(temp_number, "ID")
                    if pnumb.is_valid_number(parsed_number):
                        number_e164 = pnumb.format_number(
                            parsed_number, pnumb.PhoneNumberFormat.E164)
                    else:
                        print(
                            f"{Fore.RED}Nomor tidak valid atau format salah. Gunakan format: +62812...{Style.RESET_ALL}"
                        )
                        return
                else:
                    print(
                        f"{Fore.RED}Nomor tidak valid atau format salah. Gunakan format: +62812...{Style.RESET_ALL}"
                    )
                    return
        else:
            parsed_number = parse(number)
            if pnumb.is_valid_number(parsed_number):
                number_e164 = pnumb.format_number(parsed_number,
                                                  pnumb.PhoneNumberFormat.E164)
            else:
                print(
                    f"{Fore.RED}Nomor tidak valid. Pastikan format benar (misal: +62812...).{Style.RESET_ALL}"
                )
                return

        print(
            f"\n{Fore.GREEN}Mulai pencarian untuk nomor: {number_e164}{Style.RESET_ALL}"
        )
        check_phone_info(number_e164)

    except Exception as e:
        print(f"{Fore.RED}Gagal memproses nomor: {e}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.GREEN}Pencarian informasi nomor selesai.{Style.RESET_ALL}")


def search_tiktok_by_query(query):
    TIKTOK_API_URL = "https://xvoidofc.xvoidx.my.id/search/tiktok"
    print(
        f"\n{Fore.YELLOW}--- Mencari di TikTok berdasarkan query: '{query}' ---{Style.RESET_ALL}"
    )
    loading_animation("Mencari di TikTok...", duration=2)
    try:
        params = {"apikey": TIKTOK_API_KEY, "q": query}
        response = requests.get(TIKTOK_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status"):
            results = data.get("result", [])
            if results:
                print(
                    f"{Fore.GREEN}Ditemukan {len(results)} hasil di TikTok:{Style.RESET_ALL}"
                )
                for i, video in enumerate(results):
                    print(f"\n{Fore.CYAN}--- Video {i+1} ---{Style.RESET_ALL}")
                    print(
                        f"  {Fore.WHITE}ID Video      : {video.get('video_id')}"
                    )
                    print(
                        f"  {Fore.WHITE}Judul         : {video.get('title')}")
                    author_info = video.get('author', {})
                    print(
                        f"  {Fore.WHITE}Author        : {author_info.get('unique_id')} ({author_info.get('nickname')})"
                    )
                    print(f"  {Fore.WHITE}Link Video    : {video.get('play')}")
                    print(
                        f"  {Fore.WHITE}Jumlah Like   : {video.get('digg_count')}"
                    )
                    print(
                        f"  {Fore.WHITE}Jumlah Komen  : {video.get('comment_count')}"
                    )
                    create_time_ts = video.get('create_time')
                    if create_time_ts:
                        print(
                            f"  {Fore.WHITE}Waktu Dibuat  : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time_ts))}"
                        )
            else:
                print(
                    f"{Fore.YELLOW}Tidak ada hasil ditemukan di TikTok untuk '{query}'.{Style.RESET_ALL}"
                )
        else:
            print(
                f"{Fore.RED}Error dari API TikTok: {data.get('message', 'Pesan error tidak diketahui')}{Style.RESET_ALL}"
            )
    except requests.exceptions.RequestException as e:
        print(
            f"{Fore.RED}Error saat menghubungi API TikTok: {e}{Style.RESET_ALL}"
        )
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}Error: Respon API TikTok bukan JSON yang valid.{Style.RESET_ALL}"
        )
    except Exception as e:
        print(
            f"{Fore.RED}Terjadi kesalahan tak terduga saat mencari TikTok: {e}{Style.RESET_ALL}"
        )


def run_instagram_api_tool():
    username = input(
        f"{Fore.YELLOW}Masukkan username Instagram: {Style.RESET_ALL}").strip(
        )
    if username:
        search_instagram_by_username(username)
    else:
        print(f"{Fore.RED}Username tidak boleh kosong.{Style.RESET_ALL}")


def search_instagram_by_username(username):
    INSTAGRAM_API_URL = "https://xvoidofc.xvoidx.my.id/stalk/instagram"
    print(
        f"\n{Fore.YELLOW}--- Mencari profil Instagram: '{username}' ---{Style.RESET_ALL}"
    )
    loading_animation("Menghubungi API Instagram...", duration=2)

    try:
        params = {"apikey": "Xvoid", "user": username}
        response = requests.get(INSTAGRAM_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status"):
            result = data.get("result", {})
            print(
                f"{Fore.WHITE}Nama Akun          : {Fore.YELLOW}{result.get('name')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Username           : {Fore.YELLOW}{result.get('username')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Bio                : {Fore.YELLOW}{result.get('bio')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Jumlah Postingan   : {Fore.YELLOW}{result.get('posts')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Followers          : {Fore.YELLOW}{result.get('followers')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Following          : {Fore.YELLOW}{result.get('following')}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.WHITE}Foto Profil        : {Fore.YELLOW}{result.get('avatar')}{Style.RESET_ALL}"
            )

            save_to_file = input(
                f"\n{Fore.YELLOW}Simpan hasil ke file JSON? (y/n): {Style.RESET_ALL}"
            ).lower()
            if save_to_file == 'y':
                with open(f"{username}_profile.json", "w") as f:
                    json.dump(result, f, indent=4)
                print(
                    f"{Fore.GREEN}Data profil disimpan ke {username}_profile.json{Style.RESET_ALL}"
                )

        else:
            print(
                f"{Fore.RED}API Error: {data.get('message', 'Pesan tidak diketahui')}{Style.RESET_ALL}"
            )

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Gagal menghubungi API: {e}{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}Respon dari API bukan JSON yang valid!{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Kesalahan tak terduga: {e}{Style.RESET_ALL}")


def email_info():
    mailid = input(f"{Fore.YELLOW}Masukkan alamat email: {Style.RESET_ALL}")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", mailid):
        print(
            f"{Fore.RED}Mohon masukkan alamat email yang valid!{Style.RESET_ALL}"
        )
        return

    print(
        f"\n{Fore.YELLOW}--- Mencari informasi email untuk: {mailid} ---{Style.RESET_ALL}"
    )
    loading_animation("Menganalisis email...", duration=2)

    try:
        eml_url = f"https://ipqualityscore.com/api/json/email/{IPQUALITYSCORE_API_KEY}/{mailid}"
        eml_response = requests.get(eml_url)
        eml_response.raise_for_status()
        eml_data = eml_response.json()

        if str(eml_data.get('success')) == "False":
            print(
                f"{Fore.RED}Error dari API IPQualityScore: {eml_data.get('message', 'Pesan error tidak diketahui')}{Style.RESET_ALL}"
            )
            return

        print(f"\n{Fore.GREEN}[~] Detail E-mail:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Target E-mail       : {mailid}")
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Status Code         : {eml_response.status_code}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Valid               : {eml_data.get('valid')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Catch All           : {eml_data.get('catch_all')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Common              : {eml_data.get('common')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Deliverability      : {eml_data.get('deliverability')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Disposable          : {eml_data.get('disposable')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}DNS Valid           : {eml_data.get('dns_valid')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Fraud Score         : {eml_data.get('fraud_score')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Frequent Complainer : {eml_data.get('frequent_complainer')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Generic             : {eml_data.get('generic')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Honeypot            : {eml_data.get('honeypot')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Leaked              : {eml_data.get('leaked')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Message             : {eml_data.get('message')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Over All Score      : {eml_data.get('overall_score')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Recent Abuse        : {eml_data.get('recent_abuse')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Request ID          : {eml_data.get('request_id')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Sanitized E-mail    : {eml_data.get('sanitized_email')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}SMTP Score          : {eml_data.get('smtp_score')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Spam Trap Score     : {eml_data.get('spam_trap_score')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Success             : {eml_data.get('success')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Suggested Domain    : {eml_data.get('suggested_domain')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Suspect             : {eml_data.get('suspect')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Timed Out           : {eml_data.get('timed_out')}"
        )
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}First Name          : {eml_data.get('first_name')}"
        )

        domain_age = eml_data.get('domain_age', {})
        print(f"\n{Fore.GREEN}[~] Domain Age:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Human      : {domain_age.get('human')}")
        print(f"{Fore.CYAN}➤ {Fore.WHITE}ISO        : {domain_age.get('iso')}")
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Time Stamp : {domain_age.get('timestamp')}"
        )

        first_seen = eml_data.get('first_seen', {})
        print(f"\n{Fore.GREEN}[~] First Seen:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Human      : {first_seen.get('human')}")
        print(f"{Fore.CYAN}➤ {Fore.WHITE}ISO        : {first_seen.get('iso')}")
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Time Stamp : {first_seen.get('timestamp')}"
        )
        print(
            f"\n{Fore.GREEN}Pencarian informasi email selesai.{Style.RESET_ALL}"
        )

    except requests.exceptions.RequestException as e:
        print(
            f"{Fore.RED}Error saat menghubungi API IPQualityScore: {e}{Style.RESET_ALL}"
        )
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}Error: Respon API bukan JSON yang valid.{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Terjadi kesalahan tak terduga: {e}{Style.RESET_ALL}")


def check_nik_info():
    nik = input(f"{Fore.YELLOW}Input NIK Target: {Style.RESET_ALL}")

    if not nik.isdigit() or len(nik) != 16:
        print(f"{Fore.RED}ERROR! NIK Tidak Valid!{Style.RESET_ALL}")
        return

    provinsi_code = nik[0:2]
    kabkot_code = nik[0:4]
    kecamatan_code = nik[0:6]
    tanggal_str = nik[6:8]
    bulan = nik[8:10]
    tahun = nik[10:12]
    uniqcode = nik[12:16]

    cekjk = int(tanggal_str)
    jeniskelamin = "LAKI-LAKI" if cekjk <= 31 else "PEREMPUAN"
    if jeniskelamin == "PEREMPUAN":
        tanggal_str = str(int(tanggal_str) - 40)

    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        with open(DATA_NIK_PATH, "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        print(f"{Fore.RED}! File {DATA_NIK_PATH} tidak ditemukan.")
        print(
            f"Silakan buat file ini dengan struktur yang benar di folder 'data/'."
        )
        print(f"Contoh struktur ada di deskripsi skrip ini.{Style.RESET_ALL}")
        return
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}! Data di {DATA_NIK_PATH} tidak valid (format JSON salah) !{Style.RESET_ALL}"
        )
        return

    provinsi = data.get("provinsi", {}).get(provinsi_code, provinsi_code)
    kabkot = data.get("kabkot", {}).get(kabkot_code, kabkot_code)
    kecamatan_data = data.get("kecamatan", {}).get(kecamatan_code,
                                                   kecamatan_code)

    kecamatan_name = kecamatan_data
    kode_pos = "N/A"
    if isinstance(kecamatan_data, str) and "--" in kecamatan_data:
        kecamatan_name, kode_pos = kecamatan_data.split("--")

    print(f"\n{Fore.GREEN}--- Informasi NIK ---{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Tanggal Lahir: {tanggal_str}/{bulan}/{tahun}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Jenis Kelamin: {jeniskelamin}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Provinsi     : {provinsi}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}! {Fore.WHITE}Kab/Kota     : {kabkot}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Kecamatan    : {kecamatan_name}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Kode Pos     : {kode_pos}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}! {Fore.WHITE}Uniqcode     : {uniqcode}{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}Pencarian informasi NIK selesai.{Style.RESET_ALL}")


def check_whois(domain):
    print(
        f"\n{Fore.YELLOW}--- Mencari informasi Whois untuk domain: {domain} ---{Style.RESET_ALL}"
    )
    loading_animation("Mengambil data Whois...", duration=2)
    try:
        w = whois.whois(domain)
        if w:
            print(
                f"{Fore.GREEN}Informasi Whois untuk {domain}:{Style.RESET_ALL}"
            )
            for key, value in w.items():
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                print(
                    f"{Fore.CYAN}{str(key).replace('_', ' ').title().ljust(25)}{Style.RESET_ALL}: {Fore.WHITE}{value}"
                )
        else:
            print(
                f"{Fore.YELLOW}Tidak ada informasi Whois ditemukan untuk {domain}.{Style.RESET_ALL}"
            )
    except Exception as e:
        print(
            f"{Fore.RED}Error saat mencari Whois untuk {domain}: {e}{Style.RESET_ALL}"
        )


def check_dns_records(domain):
    print(
        f"\n{Fore.YELLOW}--- Mencari catatan DNS untuk domain: {domain} ---{Style.RESET_ALL}"
    )
    loading_animation("Mengambil catatan DNS...", duration=2)
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(
                f"\n{Fore.GREEN}Catatan {rtype} untuk {domain}:{Style.RESET_ALL}"
            )
            for rdata in answers:
                print(f"  {Fore.WHITE}{rdata}{Style.RESET_ALL}")
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            print(
                f"{Fore.RED}Domain tidak ditemukan: {domain}{Style.RESET_ALL}")
            break
        except Exception as e:
            print(
                f"{Fore.RED}Error saat mencari catatan {rtype} untuk {domain}: {e}{Style.RESET_ALL}"
            )


def run_domain_lookup_menu():
    domain = input(
        f"{Fore.YELLOW}Masukkan domain atau subdomain target (contoh: example.com): {Style.RESET_ALL}"
    )
    if not domain:
        print(f"{Fore.RED}Domain tidak boleh kosong!{Style.RESET_ALL}")
        return
    check_whois(domain)
    check_dns_records(domain)


def trace_ip():
    targetip = input(
        f"{Fore.YELLOW}Masukkan Alamat IP Target: {Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}--- Melacak IP: {targetip} ---{Style.RESET_ALL}")
    loading_animation("Memproses pelacakan IP...", duration=2)
    try:
        r = requests.get("http://ip-api.com/json/" + targetip)
        r.raise_for_status()
        data = r.json()

        print(
            f"\n{Fore.GREEN}[*] Detail IP diberikan di bawah ini:{Style.RESET_ALL}\n"
        )
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Status Code    : {r.status_code}")
        time.sleep(0.1)
        if str(data.get('status')) == 'success':
            print(
                f"{Fore.CYAN}➤ {Fore.WHITE}Status         : {Fore.GREEN}{data.get('status')}{Style.RESET_ALL}"
            )
            time.sleep(0.1)
        elif str(data.get('status')) == 'fail':
            print(
                f"{Fore.CYAN}➤ {Fore.WHITE}Status         : {Fore.RED}{data.get('status')}{Style.RESET_ALL}"
            )
            time.sleep(0.1)
            print(
                f"{Fore.CYAN}➤ {Fore.WHITE}Message        : {data.get('message')}"
            )
            time.sleep(0.1)
            if str(data.get('message')) == 'invalid query':
                print(
                    f'\n{Fore.RED}[!] {targetip} adalah Alamat IP tidak valid, Anda bisa mencoba Alamat IP lain.\n{Style.RESET_ALL}'
                )
                return
            elif str(data.get('message')) == 'private range':
                print(
                    f'\n{Fore.RED}[!] {targetip} adalah Alamat IP privat, Jadi IP ini tidak dapat dilacak.\n{Style.RESET_ALL}'
                )
                return
            elif str(data.get('message')) == 'reserved range':
                print(
                    f'\n{Fore.RED}[!] {targetip} adalah Alamat IP yang dicadangkan, Jadi IP ini tidak dapat dilacak.\n{Style.RESET_ALL}'
                )
                return
            else:
                print(
                    f'\n{Fore.RED}Periksa koneksi internet Anda.\n{Style.RESET_ALL}'
                )
                return

        print(f"{Fore.CYAN}➤ {Fore.WHITE}Target IP      : {data.get('query')}")
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Negara         : {data.get('country')}")
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Kode Negara    : {data.get('countryCode')}"
        )
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Kota           : {data.get('city')}")
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Zona Waktu     : {data.get('timezone')}"
        )
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Nama Wilayah   : {data.get('regionName')}"
        )
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Wilayah        : {data.get('region')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Kode Pos       : {data.get('zip')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Lintang        : {data.get('lat')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Bujur          : {data.get('lon')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}ISP            : {data.get('isp')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}Organisasi     : {data.get('org')}")
        time.sleep(0.1)
        print(f"{Fore.CYAN}➤ {Fore.WHITE}AS             : {data.get('as')}")
        time.sleep(0.1)
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Lokasi         : {data.get('lat')},{data.get('lon')}"
        )
        time.sleep(0.1)
        google_map_link = f"http://maps.google.com/maps?q={data.get('lat')},{data.get('lon')}"
        print(
            f"{Fore.CYAN}➤ {Fore.WHITE}Google Map     : {Fore.BLUE}{google_map_link}{Style.RESET_ALL}"
        )
        time.sleep(0.1)
        print()
        mapaddress = input(
            f"{Fore.YELLOW}[*] Tekan ENTER untuk Membuka Lokasi di Google Maps atau tekan tombol lain untuk keluar: {Style.RESET_ALL}"
        )
        if mapaddress == "":
            print(
                f"\n{Fore.GREEN}[*] Membuka Lokasi di Google Maps...{Style.RESET_ALL}\n"
            )
            webbrowser.open(google_map_link)
        else:
            print(f"\n{Fore.YELLOW}[*] Membatalkan.....{Style.RESET_ALL}\n")

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error saat melacak IP: {e}{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}Error: Respon API bukan JSON yang valid.{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Terjadi kesalahan tak terduga: {e}{Style.RESET_ALL}")


def load_site_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}File '{filepath}' tidak ditemukan.")
        print(
            f"Pastikan Anda telah membuat file 'data/sites_data.json' dengan format yang benar."
        )
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: File '{filepath}' bukan JSON yang valid.")
        return None


def check_username_on_site(username, site_name, site_info, session):
    url = site_info["url"].format(username)
    error_type = site_info["errorType"]
    error_code = site_info.get("errorCode")
    error_msg = site_info.get("errorMsg")
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    status = "Tidak Diketahui"
    profile_url = ""

    try:
        response = session.get(url,
                               headers=headers,
                               timeout=10,
                               allow_redirects=True)

        if error_type == "status_code":
            if response.status_code == 200:

                if error_msg and error_msg in response.text:
                    status = "Tersedia"
                else:
                    status = "Diklaim"
                    profile_url = url
            elif response.status_code == error_code:
                status = "Tersedia"
            else:
                status = "Tidak Diketahui"
        elif error_type == "message":
            if error_msg and error_msg in response.text:
                status = "Tersedia"
            else:
                status = "Diklaim"
                profile_url = url
        elif error_type == "response_url":
            if response.url == site_info["urlMain"]:
                status = "Tersedia"
            else:
                status = "Diklaim"
                profile_url = url
        else:
            status = "Tidak Diketahui (Error Tipe Deteksi Tidak Dikenal)"

    except requests.exceptions.RequestException as e:
        status = f"Error: {e}"
    except Exception as e:
        status = f"Kesalahan Umum: {e}"

    return site_name, status, profile_url, url


def dox_like_search(username):
    print(
        f"\n{Fore.YELLOW}--- Mencari username '{username}' di berbagai platform ---{Style.RESET_ALL}"
    )
    loading_animation("Mempersiapkan pencarian...", duration=1)

    site_data = load_site_data(SITES_DATA_PATH)
    if not site_data:
        return

    results = {}
    successful_finds = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_site = {
            executor.submit(check_username_on_site, username, site_name, info,
                            requests.Session()):
            site_name
            for site_name, info in site_data.items()
        }

        for future in as_completed(future_to_site):
            site_name = future_to_site[future]
            try:
                site_name, status, profile_url, checked_url = future.result()
                results[site_name] = {
                    "status": status,
                    "profile_url": profile_url,
                    "checked_url": checked_url
                }

                if status == "Diklaim":
                    print(
                        f"{Fore.GREEN}[+] {site_name.ljust(15)}: Diklaim! {profile_url}{Style.RESET_ALL}"
                    )
                    successful_finds.append(profile_url)
                elif "Error" in status:
                    print(
                        f"{Fore.RED}[-] {site_name.ljust(15)}: {status} ({checked_url}){Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"{Fore.YELLOW}[-] {site_name.ljust(15)}: {status} {Style.RESET_ALL}"
                    )

            except Exception as exc:
                print(
                    f"{Fore.RED}[!] {site_name.ljust(15)}: Error tak terduga: {exc}{Style.RESET_ALL}"
                )

    print(f"\n{Fore.GREEN}Pencarian username selesai.{Style.RESET_ALL}")
    if successful_finds:
        print(
            f"{Fore.CYAN}Total username ditemukan: {len(successful_finds)}{Style.RESET_ALL}"
        )
        open_browser = input(
            f"{Fore.YELLOW}Buka semua URL yang ditemukan di browser? (y/n): {Style.RESET_ALL}"
        ).lower().strip()
        if open_browser == 'y':
            for url in successful_finds:
                webbrowser.open_new_tab(url)
                time.sleep(0.5)
    else:
        print(
            f"{Fore.YELLOW}Tidak ada username ditemukan di platform yang diperiksa.{Style.RESET_ALL}"
        )


def run_dox_like_menu():
    username = input(
        f"{Fore.YELLOW}Masukkan username yang ingin Anda cari: {Style.RESET_ALL}"
    ).strip()
    if username:
        dox_like_search(username)
    else:
        print(f"{Fore.RED}Username tidak boleh kosong.{Style.RESET_ALL}")


def google_dork_phone_number():
    """Melakukan Google dorking khusus untuk nomor telepon tanpa membersihkan layar."""
    print(f"\n{RED}--- Google Dorking (Nomor Telepon) ---{RESET_ALL}")
    print(f"{DARK_GRAY}Mencari Nomor Telepon di Website{RESET_ALL}\n")

    phone_number_raw = input(
        f"{YELLOW}Masukkan nomor telepon yang ingin dicari (contoh: 6281234567890):{RESET_ALL} "
    ).strip()
    if not phone_number_raw:
        print(f"{RED}* Nomor telepon tidak boleh kosong.{RESET_ALL}")
        return

    country_code = input(
        f"{YELLOW}Masukkan kode negara (contoh: US untuk Amerika, ID untuk Indonesia):{RESET_ALL} "
    ).strip().upper()
    if not country_code:
        print(f"{RED}* Kode negara tidak boleh kosong.{RESET_ALL}")
        return

    try:
        parsed_number = pnumb.parse(phone_number_raw, country_code)
        if not pnumb.is_valid_number(parsed_number):
            print(
                f"{RED}* Nomor telepon atau kode negara tidak valid. Pastikan format benar.{RESET_ALL}"
            )
            return

        formats = [
            pnumb.format_number(parsed_number, pnumb.PhoneNumberFormat.E164),
            pnumb.format_number(parsed_number,
                                pnumb.PhoneNumberFormat.INTERNATIONAL),
            pnumb.format_number(parsed_number,
                                pnumb.PhoneNumberFormat.NATIONAL).replace(
                                    " ", "-"),
            pnumb.format_number(parsed_number,
                                pnumb.PhoneNumberFormat.NATIONAL).replace(
                                    " ", ""),
        ]

        if phone_number_raw.startswith(str(parsed_number.country_code)):
            formats.append(
                phone_number_raw[len(str(parsed_number.country_code)):])

        dork_terms = list(set([f'intext:"{f}"' for f in formats if f]))

        print(f"{WHITE}{LINES_SEPARATOR}{RESET_ALL}")
        print(
            f"{RED}Mencari hasil untuk nomor: {YELLOW}{phone_number_raw} ({country_code}){RESET_ALL}"
        )
        print(
            f"{RED}Menggunakan dork: {YELLOW}{', '.join(dork_terms)}{RESET_ALL}"
        )
        urls_found = []

        loading_animation("Memulai pencarian Google...", duration=1)

        for dork_query in dork_terms:
            try:
                for result_url in search(dork_query, num=10, stop=10, pause=2):
                    if result_url not in urls_found:
                        urls_found.append(result_url)
            except Exception as e_search:
                print(
                    f"{RED}* Terjadi kesalahan saat pencarian Google untuk '{dork_query}': {e_search}{RESET_ALL}"
                )

        if not urls_found:
            print(
                f"{YELLOW}* Tidak ada hasil ditemukan untuk nomor '{phone_number_raw}'.{RESET_ALL}"
            )
            return

        print(
            f"{GREEN}Berhasil menemukan {len(urls_found)} URL unik.{RESET_ALL}"
        )
        print(f"Menganalisis hasil...{RESET_ALL}")

        for idx, result_url in enumerate(urls_found):
            try:
                req = requests.get(result_url, headers=HEADERS, timeout=10)
                req.raise_for_status()
                res_content = fromstring(req.content)
                title_text = res_content.findtext(".//title")

                if title_text:
                    wrapper = textwrap.TextWrapper(width=47)
                    dedented_text = textwrap.dedent(text=title_text)
                    shortened_text = textwrap.shorten(
                        text=wrapper.fill(text=dedented_text),
                        width=47,
                        placeholder="...")
                    formatted_title = wrapper.fill(text=shortened_text)
                    print(
                        f"{BG_BLUE_SIMULATED} FOUND {WHITE} {formatted_title}{RESET_ALL}\n"
                        f"{DARK_GRAY}{result_url}{RESET_ALL}")
                else:
                    print(
                        f"{BG_BLUE_SIMULATED} FOUND {WHITE} [No Title Found]{RESET_ALL}\n"
                        f"{DARK_GRAY}{result_url}{RESET_ALL}")

            except requests.exceptions.HTTPError as http_err_dork:
                print(
                    f"{RED}* HTTP error mengakses {result_url}: {http_err_dork}{RESET_ALL}"
                )
            except requests.exceptions.RequestException as req_err_dork:
                print(
                    f"{RED}* Kesalahan permintaan saat mengakses {result_url}: {req_err_dork}{RESET_ALL}"
                )
            except TypeError:
                print(
                    f"{YELLOW}* Tidak dapat mengurai judul untuk {result_url}{RESET_ALL}"
                )
            except KeyboardInterrupt:
                print(f"{RED}* Dorking dibatalkan oleh pengguna.{RESET_ALL}")
                break
            finally:
                pass

    except Exception as e:
        print(f"{RED}* Terjadi kesalahan umum: {e}{RESET_ALL}")

    print(f"{WHITE}{LINES_SEPARATOR}{RESET_ALL}")
    print(f"{BLUE}> {WHITE}Pencarian nomor telepon selesai.{RESET_ALL}")


def print_main_menu_options():
    print_banner()
    print(f"{Fore.RED}Pilih fitur yang ingin Anda gunakan:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Cek Informasi Nomor Telepon")
    print(f"2. Cek Sosial Media (TikTok, Instagram)")
    print(f"3. Cek Informasi Email")
    print(f"4. Cek Informasi NIK")
    print(f"5. Cek Informasi Domain/IP")
    print(f"6. Cari Username")
    print(f"7. Google Dorking (Nomor Telepon){Style.RESET_ALL}")
    print(f"0. Keluar{Style.RESET_ALL}")
    print(
        f"{Fore.RED}=========================================={Style.RESET_ALL}"
    )


def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        print(f"{Fore.YELLOW}Direktori 'data/' telah dibuat.{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Pastikan file 'data/data.json' ada untuk fungsi NIK dan 'data/sites_data.json' untuk fitur baru.{Style.RESET_ALL}"
        )
        input(
            f"{Fore.MAGENTA}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")

    if not os.path.exists(SITES_DATA_PATH):
        print(
            f"{Fore.YELLOW}File '{SITES_DATA_PATH}' tidak ditemukan. Membuat file default...{Style.RESET_ALL}"
        )
        default_sites_data = {"key": "value"}
        with open(SITES_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_sites_data, f, indent=4)
        print(
            f"{Fore.GREEN}File 'data/sites_data.json' telah dibuat dengan data default. Anda bisa mengeditnya.{Style.RESET_ALL}"
        )
        input(
            f"{Fore.MAGENTA}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")

    while True:
        print_main_menu_options()
        choice = input(
            f"{Fore.YELLOW}Masukkan pilihan Anda: {Style.RESET_ALL}").strip()

        if choice == '1':
            run_phone_lookup_menu()
        elif choice == '2':
            print(
                f"\n{Fore.GREEN}Pilih platform Sosial Media:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  a. TikTok (berdasarkan query)")
            print(f"{Fore.WHITE}  b. Instagram (berdasarkan username)")
            sm_choice = input(f"{Fore.YELLOW}Pilihan (a/b): {Style.RESET_ALL}"
                              ).lower().strip()
            if sm_choice == 'a':
                query = input(
                    f"{Fore.YELLOW}Masukkan query (nama pengguna, nomor, dll.): {Style.RESET_ALL}"
                )
                search_tiktok_by_query(query)
            elif sm_choice == 'b':
                run_instagram_api_tool()
            else:
                print(f"{Fore.RED}Pilihan tidak valid.{Style.RESET_ALL}")
        elif choice == '3':
            email_info()
        elif choice == '4':
            check_nik_info()
        elif choice == '5':
            print(
                f"\n{Fore.GREEN}Pilih jenis pencarian Domain/IP:{Style.RESET_ALL}"
            )
            print(f"{Fore.WHITE}  a. Whois/DNS Lookup")
            print(f"{Fore.WHITE}  b. IP Trace")
            net_choice = input(f"{Fore.YELLOW}Pilihan (a/b): {Style.RESET_ALL}"
                               ).lower().strip()
            if net_choice == 'a':
                run_domain_lookup_menu()
            elif net_choice == 'b':
                trace_ip()
            else:
                print(f"{Fore.RED}Pilihan tidak valid.{Style.RESET_ALL}")
        elif choice == '6':
            run_dox_like_menu()
        elif choice == '7':
            google_dork_phone_number()
        elif choice == '0':
            print(
                f"{Fore.GREEN}Terima kasih telah menggunakan alat OSINT. Sampai jumpa!{Style.RESET_ALL}"
            )
            sys.exit()
        else:
            print(
                f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}"
            )

        if choice != '0':
            input(
                f"\n{Fore.MAGENTA}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}"
            )


if __name__ == "__main__":
    main()
