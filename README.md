# Google Scraper

This project contains a script to scrape Google SERP (Search Engine Results Pages).

## Files

- `google_serp_scrape.py`: The main script for scraping Google SERP.
- `requirements.txt`: List of dependencies required to run the script.

## Setup

### Create a Virtual Environment

It's a good practice to run your Python projects in a virtual environment to manage dependencies and avoid conflicts with other projects.

#### On Windows

1. Open Command Prompt (cmd) or PowerShell.
2. Navigate to the project directory:
    cd path\to\your\project\Google_Scraper
3. Create a virtual environment named `venv`:
    python -m venv venv
4. Activate the virtual environment:
    .\venv\Scripts\activate

#### On Mac

1. Open Terminal.
2. Navigate to the project directory:
    cd /path/to/your/project/Google_Scraper
3. Create a virtual environment named `venv`:
    python3 -m venv venv
4. Activate the virtual environment:
    source venv/bin/activate

### Install Dependencies
1. Once the virtual environment is activated, install the required dependencies:
    pip install -r requirements.txt

### Run the Script

1. Run the script:
    python google_serp_scrape.py

### Extra Notes

1. You can change the query to be whatever you want to search on google.
2. You can change the number of pages you want to scrape on google by adjusting that in the second paramater of the function call to search().