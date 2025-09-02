# Media Tools

This repository contains tools for collecting and processing article URLs and saving and evaluating web content. It uses the LegoNews's PublisherMetaJSONExporter's output format as input.

## Overview

- **save_content.py**: Reads article URLs from PublisherMetaJSONExporter's JSON files, downloads web pages using Playwright, and saves the HTML content. Handles retries, error logging, and parallel processing.
- **collect_site_urls.py**: Aggregates URLs from result files, checks for 404 missing error, and outputs a CSV with problem flags. Uses multiprocessing for faster processing. Modify function check_404 for different site specific error
404 messages.

Both scripts are configurable via a `config.ini` file.

---

## save_content.py

**Purpose:**  
- Reads article URLs from JSON files.
- Downloads and saves web pages using Playwright.
- Handles retries, error logging, and parallel downloads.

**Key Features:**
- Uses Playwright for robust web scraping.
- Multiprocessing for parallel downloads.
- Handles failed downloads and logs problematic files.
- Removes unwanted URL suffixes.

**Configurable via:**  
- `INPUT_FOLDER_PATTERN`: Glob pattern for input JSON files.
- `OUTPUT_FOLDER`: Where to save downloaded HTML files.
- `MAX_RETRY`: Number of retry attempts for failed downloads.
- `RETRY_WAIT_TIME`: Wait time between retries (seconds).
- `DIR_MAX_FILES`: Max files per output folder. (don't modify!)
- `CORES`: Number of parallel processes. ONLY SET HIGHER IF THERE ARE MANY DIFFERENT SITES! The urls are randomized into equal chunks, to not query the same site many times. With a single site it will cause the site to block the too many queries!

---

## collect_site_urls.py

**Purpose:**  
- Reads result files from the output directory.
- Checks if downloaded articles contain a specific error message.
- Flags problematic articles and outputs a summary CSV.

**Key Features:**
- Multiprocessing for faster row-wise checks.
- Configurable site name, input path, and number of workers.
- Outputs `Articles.csv` with a `problem` column indicating error pages.

**Configurable via:**  
- `SITE_NAME`: The domain to filter URLs.
- `INPUT_PATH`: Path to the result files.
- `NUM_WORKERS`: Number of parallel processes.

---

## Usage

1. **Install dependencies:**
   ```sh
   pip install pandas numpy tqdm requests playwright
   python -m playwright install
   ```

2. **Edit `config.ini`** with your desired settings.

3. **Run the scripts:**
   ```sh
   python collect_site_urls.py
   python save_content.py
   ```

---

## Notes

- Ensure your virtual environment is activated before running the scripts.
- Output and error files are written to the `output/` directory.
- For Windows batch automation, you can use a `.bat` file:
  ```bat
  @echo off
  call venv\Scripts\activate
  python collect_site_urls.py
  python save_content.py
  pause
  ```

---

## License

MIT License (add your license here)