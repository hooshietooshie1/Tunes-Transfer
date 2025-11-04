import requests, random, json
def download_image(img_url: str):
    response = requests.get(img_url)
    output_file = "temp_img.jpeg"
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded and saved as: {output_file}")
        return output_file
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
        return False
    
def generate_random_name():
    import requests
    languages = ["en"]
    case = ["", "&type=uppercase", "&type=lowercase", "&type=capitalized"]
    url = "https://random-words-api.kushcreates.com/api"
    response = requests.get(url)
    if response.status_code != 200:
        exit('no')
    w1 = requests.get(f"{url}?language={random.choice(languages)}{random.choice(case)}&words=1").json()[0]['word']
    w2 = requests.get(f"{url}?language={random.choice(languages)}{random.choice(case)}&words=1").json()[0]['word']
    playlist_name = f"{w1} {w2}"
    print("Random Playlist Name: " + playlist_name + '\n')
    return playlist_name

def pretty_print(log: any, indent: int = 1):
    print(json.dumps(log, indent=indent))

def print_song_deets(song_obj):
        print(f"Song ID: {song_obj.get_song_id()} \n" \
                f"Title: {song_obj.get_song_title()} \n" \
                f"Artists: {song_obj.get_song_artists_list()} \n" \
                f"Album: {song_obj.get_song_album_name()} \n" \
                f"Album ID: {song_obj.get_song_album_id()} \n" \
                f"Year: {song_obj.get_song_year()} \n" \
                f"Duration: {song_obj.get_song_duration_secs()} \n")
        
def pick_best_match(platform: str, results, track_name, artist_name):
    from difflib import SequenceMatcher

    best_score = 0
    best_result = None

    for r in results:
        if platform.lower() == 'youtube':
            title = r.get("title", "").lower()
            artist = ", ".join(a["name"] for a in r.get("artists", []))
            combined = f"{title} {artist}".lower()
            artist_name = ' '.join(artist_name)
        elif platform.lower() == 'spotify':
            title = r.get("name", "").lower()
            artist = ", ".join(a["name"] for a in r.get("artists", []))
            combined = f"{title} {artist}".lower()
            artist_name = ' '.join(artist_name)

        # Fuzzy match score
        score = SequenceMatcher(None, combined, f"{track_name.lower()} {artist_name.lower()}").ratio()

        if score > best_score:
            best_score = score
            best_result = r

    return best_result


# mostly chatGPT BS to fetch the headers, YT Music API is kinda caveman brain
def get_yt_headers_auth():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException
    from pathlib import Path
    from .exceptional import ClassicException
    import json
    import time
    import hashlib
    import time
    import os
    import tempfile
    import chromedriver_autoinstaller

    COOKIES_FILE = Path("ytmusic_cookies.json")

    def get_sapisidhash_auth(sapisid_cookie: str, origin="https://music.youtube.com"):
        timestamp = int(time.time())
        input_str = f"{timestamp} {sapisid_cookie} {origin}"
        sha1_hash = hashlib.sha1(input_str.encode("utf-8")).hexdigest()
        return f"SAPISIDHASH {timestamp}_{sha1_hash}"


    def check_user_login(driver_o: webdriver.Chrome):
        cookies = {c['name']: c['value'] for c in driver_o.get_cookies()}
        has_auth_cookie = any(name in cookies for name in ("SAPISID", "APISID", "HSID", "SID"))

        if has_auth_cookie:
            return True
        else:
            return False
        
    def evaluate_headers_auth(cookies, driver: webdriver.Chrome):
        sapisid = None
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        for part in cookie_str.split(';'):
            if part.strip().startswith("SAPISID="):
                sapisid = part.strip().split("=", 1)[1]
                break

        if sapisid:
            sapisid_header = get_sapisidhash_auth(sapisid)
        else:
            raise ClassicException(msg='ERROR getting SAPIS ID', err_code=90)

        # print("YT Music login successful!")
        headers = {
            "Authorization": sapisid_header,
            "User-Agent": driver.execute_script("return navigator.userAgent;"),
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Goog-AuthUser": "0",
            "x-origin": "https://music.youtube.com",
            "Cookie": cookie_str,
        }

        path = "headers_auth.json"
        with open(path, "w",) as f:
            json.dump(headers, f, indent=2)

        print(f"Auth headers saved to {path}")

    def get_stable_chrome_driver(existing_profile=True):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-blink-features=AutomationControlled")

        if existing_profile:
            user_data_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
            options.add_argument(f"user-data-dir={user_data_dir}")
            options.add_argument("profile-directory=Default")
        else:
            options.add_argument(f"user-data-dir={tempfile.mkdtemp()}")

        driver = webdriver.Chrome(options=options)
        return driver
    

    def open_ytmusic_with_existing_login(url: str = "https://music.youtube.com/"):
        """
        Opens YouTube Music in user's existing Chrome session if possible.
        Falls back to system default browser if Chrome unavailable.
        Automatically saves and reuses cookies between runs.

        Returns True if login was detected (cookies found), False otherwise.
        """

        print("Launching YouTube Music...")
        chromedriver_autoinstaller.install()
        # --- If cookies exist, reuse them via Selenium headless ---
        if COOKIES_FILE.exists():
            print("Found existing cookies — attempting to reuse session.")
            try:
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")

                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)

                # Load saved cookies
                with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                    for c in cookies:
                        driver.add_cookie(c)

                driver.refresh()
                time.sleep(3)

                # Verify login (check if "Sign in" is missing)
                if check_user_login(driver):
                    print("Login verified using saved cookies.")
                    ret_cookies = driver.get_cookies()
                    evaluate_headers_auth(ret_cookies, driver)
                    print("Saving new cookies...")
                    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                        json.dump(driver.get_cookies(), f, indent=2)
                    driver.quit()
                    return True

                driver.quit()
            except Exception as e:
                print(f"Cookie reuse failed: {e}")

        # --- Try using user's existing Chrome profile ---
        print("Opening Chrome using your default profile...")
    
        try:
            driver = get_stable_chrome_driver()
            driver.get(url)
        except Exception as e:
            print("Chrome failed with default profile, retrying with clean profile")
            driver = get_stable_chrome_driver(False)
            driver.get(url)

        while True:
            try:
                if check_user_login(driver):
                    print("Login detected!")
                    ret_cookies = driver.get_cookies()
                    evaluate_headers_auth(ret_cookies, driver)
                    print("Saving new cookies...")
                    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                        json.dump(driver.get_cookies(), f, indent=2)
                    driver.quit()
                    return ret_cookies
                time.sleep(2)
            except WebDriverException:
                print("Browser closed...")
                break

    # save cookies
    yt_login = open_ytmusic_with_existing_login()
    if not yt_login:
        raise ClassicException("Login not detected — please ensure you're logged into YouTube Music.", 90)
