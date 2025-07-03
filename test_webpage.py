import pandas as pd
from playwright.sync_api import sync_playwright
import json
import time

# 0 for json input
TEST = 0
MAX_RETRY = 3
RETRY_WAIT_TIME = 10
INPUT_JSON = "7991.json"

def check_google_fail(browser) :
    g_page = browser.new_page()
    try:
        resp = g_page.goto("https://google.com", wait_until="domcontentloaded", timeout=15000)
        return 0
    except Exception as e:
        return 1
    
def check_main_site(site, browser) :
    g_page = browser.new_page()
    try:
        resp = g_page.goto("https://" + site, wait_until="domcontentloaded", timeout=15000)
        return 0
    except Exception as e:
        return 1

def get_main_site(string) :
    return_string = string[string.find("//")+2:] + "/"
    return return_string[:return_string.find("/")]


if (TEST == 0) :

    with open("input/" + INPUT_JSON, "r", encoding="utf-8") as file:
        data = json.load(file)

    key = data.keys()
    print(key)

    urls = data["articleIndex"].keys()
    urls = ["https://" + string for string in urls ]
    

if TEST != 0 :
    urls = [
        "https://example.com",
        "https://index.hu/belfold/2025/07/02/japan-szamuraj-kodex-konyv-ajanlo-hagyomany-strategia-vilag-harcos-filozofia/",
        "https://example.com/missing-page",
        "https://index.hu/asdadasdadasd",
        "https://index.hu/belfold/2025/07/02/japan-szamuraj-kodex-konyv-ajanlo-hagyomany-strategia-vilag-harcos-filozofia/",
        "https://index.hu/belfold/2025/07/02/snasbfaofnaf",
        "https://www.bbc.com/news/av/world-46722127233"
    ]

done_urls = set()
try:
    with open("temp/" + INPUT_JSON[:-5] + ".csv", "r", encoding="utf-8") as text_file:
        for line in text_file:
            print(line)
            done_urls.add(line[:-1])
except:
    pass

result = []
error = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    for url in urls:
        if url in done_urls:
            print("Already done: " + url)
            continue
        retry = 1
        retry_count = 0
        while(retry_count < MAX_RETRY and retry == 1) :
            retry = 0
            er = ""
            try:
                page = browser.new_page()
                response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
                # Wait until the final navigation settles
                final_url = page.wait_for_url("**", timeout=15000)
                if not page.locator("h1").is_visible() :
                    print(f"{url} — Content MISSING")
                    flag = 0
                # TEST FOR BBC add more sphisticated test later?
                elif "Sorry, we couldn’t find that page" in page.locator("h1").text_content() :
                    print(f"{url} — Content MISSING")
                    flag = 0
                else :
                    print(f"{url} — Content OK")
                    flag = 1
            except Exception as e:
                print(f"{url} — ERROR: {e}")
                problem = 1
                #Check if internet or main site problem, wait for it to resolve
                while(problem):
                    time.sleep(RETRY_WAIT_TIME)
                    google_fail = check_google_fail(browser)
                    main_site_fail  = check_main_site(get_main_site(url), browser)
                    print("Connection issue: " + str(google_fail))
                    print("Able to reach " + get_main_site(url) +": " + str(main_site_fail))
                    problem = google_fail or main_site_fail
                retry = 1
                retry_count = retry_count + 1
                flag = 0
                er = e
        result.append(flag)
        error.append(er)
        with open("output/" + INPUT_JSON[:-5] + ".csv", "a", encoding="utf-8") as text_file:
            text_file.write(str(flag)+";"+str(er=="")+";"+ url+"\n")

        with open("temp/" + INPUT_JSON[:-5] + ".csv", "a", encoding="utf-8") as text_file:
            text_file.write(url+"\n")


    browser.close()
    print(result)
    print(error)

