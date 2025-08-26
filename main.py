import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from requests_html import HTMLSession
import re
from email_validator import validate_email, EmailNotValidError
from camoufox.async_api import AsyncCamoufox
import pandas as pd
import os

import argparse


def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive integer" % value)
    return ivalue

parser = argparse.ArgumentParser(description='Process some inputs.')

parser.add_argument(
    "-q", "--query",
    type=str,
    required=True,
    help="Search Query (required)"
)

# Optional limit argument with -lm and --limit
parser.add_argument(
    "-l", "--limit",
    type=positive_int,
    default=1,
    help="Limit of pages (default: 1)"
)
args = parser.parse_args()




async def google_search(query, limit):
    async with AsyncCamoufox() as browser:

        context = await browser.new_context(
            locale='en-US',
            geolocation={"longitude": 41.890221, "latitude": 12.492348},
        )
        page = await context.new_page() 

        #await stealth_async(page)
        encoded_query = quote_plus(query.strip())
        await page.goto(f"https://www.google.com/search?q={encoded_query}")
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(10)


        # Extracting the page content
        urls = []
        page_number = 1
        while True:
            links = await page.query_selector_all('a.zReHs')
            
            for link in links:
                url = await link.get_attribute('href')
                if 'google' not in url and 'map' not in url and 'facebook' not in url:
                    urls.append(url)

            if page_number > limit:
                break


            page_number = page_number + 1
            # click next button
            next_button = await page.query_selector(f'a[aria-label="Page {page_number}"]')
            if next_button:
                await next_button.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(5)
            else:
                break

        return urls



def scrape_emails(url):

    # get html page
    
    try:
        session = HTMLSession()
        response = session.get(url) # send a GET request to the url
        soup = BeautifulSoup(response.content, 'html.parser') # extract the html content
        page_html = soup.prettify()
    except:
        return []
    
    # get website title
    title_el = soup.select_one('title')
    if title_el is None:
        title = ''
    else:
        title = title_el.text.strip()

    emails = []
    # Matching against the email structure:
    email_pattern = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})')
    email_matches = re.findall(email_pattern, page_html)
    for email in email_matches:
        emails.append(email)
    
    # Matching against emails links with mailto: text
    email_matches = soup.select('a[href^="mailto:"]')
    for email in email_matches:
        href = email['href']
        href = href.replace('mailto:','').strip()
        emails.append(href)
    
    validated_emails = []
    # validate emails
    for email in list(set(emails)):
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
            validated_emails.append(email)
        except EmailNotValidError as e:
            continue
    
    # matching phone numbers
    phones = []
    phone_links = soup.find_all('a', href=lambda href: href and href.startswith('tel:'))
    phone_matches = [link['href'].replace('tel:', '') for link in phone_links]
    
    for phone in phone_matches:
        if phone != '':
            phones.append(phone)

    

    result = {
        'title' : title,
        'url' : url,
        'emails': validated_emails,
        'phones' : list(set(phones))
    }
        
    return result


def main(search_query, location, limit):
    
    urls = asyncio.run(google_search(f"{search_query} {location} -blog -forum -linkedin -glassdoor -indeed -facebook -reddit", limit = limit))
    # scrape 
    data = []
    for url in urls:
        results = scrape_emails(url)
        if results:
            if results['emails'] != [] or results['phones'] != []:
                data.append(results)
                
    
    return data


def store(data):
    # Load existing CSV
    csv_file = "emails.csv"
    
    # Check if file exists
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        # Create empty DataFrame with the columns you expect
        df = pd.DataFrame(columns=["title", "url", "emails","phones"])
    
    # Convert new data into DataFrame
    new_df = pd.DataFrame(data)
    
    # Merge: update existing rows and append new ones
    # 'url' is the unique key
    df = pd.concat([df, new_df]).drop_duplicates(subset=["url"], keep="last")

    # Save back to CSV
    df.to_csv(csv_file, index=False)

data = main(args.query, "", args.limit)
print(data)
store(data)


