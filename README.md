<div id="top"></div>
<div align="center">
  <h1 align="center">Email Extractor</h1>
</div>

A Python script that takes a search query, performs a Google search, visits all websites in the search results, and extracts **email addresses** and **phone numbers** found on those pages.

  <br>

## ⚙️ Features

- 🔍 Accepts any search query
- 🌐 Scrapes Google Search results
- 🕸️ Crawls each result URL
- ✉️ Extracts email addresses
- 📞 Extracts phone numbers (basic regex-based)
- 💾 Saves the extracted data to a file or displays it in the console

  <br>

## 🚀 How It Works

1. You enter a search query (e.g., `graphic designers in New York`)
2. The script uses Google Search to retrieve the top results
3. It visits each link and scrapes the page content
4. Regex is used to extract valid email addresses and phone numbers
5. Outputs the results in csv file


<!-- GETTING STARTED -->
## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/sarrarmohcin/Email-Extractor.git
   ```
2. Install requirements
   ```sh
   pip install -r requirements.txt
   ```
3. Install Camoufox
   View Camoufox Docs : https://camoufox.com/python/installation/
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

python main.py --search "graphic designers in New York" --limit 2

--search : search query (required)
--limit : Limit number of pages (must be > 0, required)

<p align="right">(<a href="#top">back to top</a>)</p>


