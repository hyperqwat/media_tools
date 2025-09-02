import glob
from tqdm import tqdm
import requests
import json
from playwright.sync_api import sync_playwright
import os
import time
import multiprocessing
import random
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
INPUT_FOLDER_PATTERN = config['save_content']['INPUT_FOLDER_PATTERN']
OUTPUT_FOLDER = config['save_content']['OUTPUT_FOLDER']
MAX_RETRY = config.getint('save_content', 'MAX_RETRY')
RETRY_WAIT_TIME = config.getint('save_content', 'RETRY_WAIT_TIME')
DIR_MAX_FILES = config.getint('save_content', 'DIR_MAX_FILES')
cores = config.getint('save_content', 'CORES')

def remove_weird_suffix(url):
    url = url.removesuffix("/&cc=cikkszerzonek@mail.index.nemspa_m.hu")
    return url

def read_input_urls(json_list, url_list) :
    for json_file in json_list:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        try :
            urls = data["articleIndex"].keys()
            urls = ["https://" + remove_weird_suffix(string) for string in urls ]
            url_list.extend(urls)
        except :
            write_problematic_file(json_file)

def read_done_urls(urls_set) :
    try:
        with open("output/raw_done.csv", "r", encoding="utf-8") as text_file:
            for line in text_file:
                print(line)
                urls_set.add(line[:-1])
    except:
        pass
    return

def read_done_urls_cores(urls_set) :
    for i in range(20) :
        try:
            with open("output/raw_done" + str(i) + ".csv", "r", encoding="utf-8") as text_file:
                for line in text_file:
                    print(line)
                    urls_set.add(line[:-1])
        except:
            pass
    return

def write_done_url(done_url) :
    with open("output/raw_done.csv", "a", encoding="utf-8") as text_file:
        text_file.write(done_url+"\n")

def write_failed_url(failed_url, core) :
    with open("output/failed_pages" + str(core) + ".csv", "a+") as fail:
        fail.write(str(failed_url)+"\n")

def write_problematic_file(failed_file) :
    with open("output/failed_files.csv", "a+") as fail:
        fail.write(str(failed_file)+"\n")

def check_google_fail(browser) :
    g_page = browser.new_page()
    try:
        resp = g_page.goto("https://google.com", wait_until="domcontentloaded", timeout=15000)
        return_value = 0
    except Exception as e:
        return_value = 1
    g_page.close()
    return return_value

def check_main_site(site, browser) :
    g_page = browser.new_page()
    try:
        resp = g_page.goto("https://" + site, wait_until="domcontentloaded", timeout=15000)
        return_value = 0
    except Exception as e:
        return_value = 1
    g_page.close()
    return return_value

def get_main_site(string) :
    return_string = string[string.find("//")+2:] + "/"
    return return_string[:return_string.find("/")]

def get_file_counter() :
    with open("output/results.csv", "r") as file:
        for line in file :
            pass
        last_line = line
    end = last_line.find(";")
    return last_line[0:end]
    
def chunkify(lst,n):
    return [ lst[i::n] for i in range(n) ]

def save_pages(to_read_urls, core, done_urls) :

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            with open("output/results" + str(core) + ".csv", "r") as file:
                for line in file :
                    pass
                last_line = line
                end = last_line.find(";")
                file_counter =  int(last_line[0:end])
                last_line = last_line[end+1:]
                end = last_line.find(";")
                folder_counter = int(last_line[0:end])
        except:
            file_counter = 0
            folder_counter = 0


        for url in tqdm(to_read_urls, "Saving webpages...") :
            if url in done_urls:
                continue
            retry = 1
            retry_count = 0
            fail = 0
            while(retry_count < MAX_RETRY and retry == 1) :
                retry = 0
                try:
                    page = browser.new_page()
                    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                    # Wait until the final navigation settles
                    final_url = page.wait_for_url("**", timeout=15000)

                    #SAVE CONTENT
                    folder_path = OUTPUT_FOLDER + str(folder_counter) + "_" + str(core) + "/"
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    save_path = folder_path + str(file_counter) + ".csv"
                    with open(save_path, "w", encoding="utf-8") as output_html:
                        output_html.write(page.content())

                    with open("output/results" + str(core) + ".csv", "a", encoding="utf-8") as text_file:
                        text_file.write(str(file_counter)+";"+str(folder_counter)+";"+ url+"\n")

                    with open("output/raw_done" + str(core) + ".csv", "a", encoding="utf-8") as text_file:
                        text_file.write(url+"\n")

                    file_counter = file_counter + 1 
                    if file_counter >= DIR_MAX_FILES:
                        folder_counter = folder_counter + 1
                        file_counter = 0

                except Exception as e:
                    problem = 1
                    problem_counter = 0
                    #Check if internet or main site problem, wait for it to resolve
                    while(problem):
                        time.sleep(RETRY_WAIT_TIME)
                        google_fail = check_google_fail(browser)
                        main_site_fail  = check_main_site(get_main_site(url), browser)
                        print("Connection issue: " + str(google_fail))
                        print("Able to reach " + get_main_site(url) +": " + str(main_site_fail))
                        problem = google_fail or main_site_fail
                        
                        if (main_site_fail and not google_fail):
                            problem_counter = problem_counter + 1
                        
                        if (problem_counter >= 1) :
                            problem = 0

                    retry = 1
                    retry_count = retry_count + 1
                    if (retry_count >= MAX_RETRY) :
                        fail = 1
                        write_failed_url(url, core)
                page.close()




if __name__ == '__main__' :


    files = glob.glob(INPUT_FOLDER_PATTERN, recursive=True)

    done_urls = set()
    to_read_urls = []
    read_input_urls(files, to_read_urls)
    read_done_urls(done_urls)
    read_done_urls_cores(done_urls)

    print(str(len(to_read_urls))+"\n") 
    to_read_urls = list(dict.fromkeys(to_read_urls))
    print(str(len(to_read_urls))+"\n") 
    random.shuffle(to_read_urls)
    lists = chunkify(to_read_urls, cores)

    for i in range(cores):
        globals()['p_%d' % i]=multiprocessing.Process(target=save_pages, args=(lists[i], i, done_urls))
        globals()['p_%d' % i].start()
    for i in range(cores):
        globals()['p_%d' % i].join()



