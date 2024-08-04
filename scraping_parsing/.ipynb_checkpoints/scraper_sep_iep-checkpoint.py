#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().run_line_magic('pip', 'install requests beautifulsoup4 fpdf')


# In[ ]:





# In[1]:


import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def fetch_article_links(contents_url):
    # Fetch the content from the URL
    response = requests.get(contents_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the content. Status code: {response.status_code}")
        return []

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    # Find all article links
    article_links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Print out each href to debug
        # print(f"Found link: {href}")
        
        # Fix malformed URLs
        if href.startswith('/entries/') or href.startswith('entries/'):
            full_url = urljoin('https://plato.stanford.edu/', href)
            if 'https://plato.stanford.edu/' in full_url:
                article_links.append(full_url)
        elif href.startswith('http') and 'plato.stanford.edu' in href:
            article_links.append(href)
    
    # Remove duplicates
    article_links = list(set(article_links))
    
    return article_links

# Example usage
contents_url = 'https://plato.stanford.edu/contents.html'
article_links = fetch_article_links(contents_url)
print(f"Found {len(article_links)} article links.")


# Save the links to a JSON file
with open('article_links_sep.json', 'w') as file:
    json.dump(article_links, file, indent=4)
    print("Saved")




# In[4]:


import requests
from bs4 import BeautifulSoup
import json
import os
import re

def fetch_and_save_articles_from_file(links_file, output_dir):
    # Load article links from the JSON file
    with open(links_file, 'r') as file:
        article_links = json.load(file)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, link in enumerate(article_links):
        # Adjust link to be absolute if necessary
        if not link.startswith('http'):
            link = f'https://plato.stanford.edu{link}'
        
        try:
            response = requests.get(link)
            if response.status_code != 200:
                print(f"Failed to retrieve article from {link}. Status code: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)

            # Extract the article title
            title_tag = soup.find('title')
            title = title_tag.get_text() if title_tag else f'article_{i+1}'
            
            # Sanitize the title to create a valid filename
            title = re.sub(r'[\\/*?:"<>|]', "", title)
            filename = os.path.join(output_dir, f"{title}.txt")
            
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(text)
            
            print(f"Saved article {i+1} to {filename}")
        
        except Exception as e:
            print(f"Error processing {link}: {e}")

# Example usage
links_file = 'article_links_sep.json'
output_dir = 'articles_text/SEP/'
fetch_and_save_articles_from_file(links_file, output_dir)


# In[7]:


import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin

# Step 1: Fetch Article Links
def fetch_article_links(contents_url):
    response = requests.get(contents_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the content. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    article_links = []
    base_url = 'https://iep.utm.edu/'

    # Find and navigate through alphabetical index
    for letter in range(ord('A'), ord('Z') + 1):
        letter_url = urljoin(base_url, chr(letter).lower() + '/')
        #print(f"Processing index page: {letter_url}")  # Debugging line
        
        letter_response = requests.get(letter_url)
        if letter_response.status_code != 200:
            print(f"Failed to retrieve the index page {letter_url}. Status code: {letter_response.status_code}")
            continue
        
        letter_soup = BeautifulSoup(letter_response.text, 'html.parser')
        
        # Extract article links from the index page
        for a_tag in letter_soup.select('li a'):
            article_href = a_tag.get('href')
            full_url = urljoin(base_url, article_href)
            article_links.append(full_url)
            #print(f"Found article link: {full_url}")  # Debugging line
    
    # Remove duplicates
    article_links = list(set(article_links))
    
    return article_links


# Example usage
contents_url = 'https://iep.utm.edu/'
article_links = fetch_article_links(contents_url)
#print(f"Found {len(article_links)} article links.")
# Save the links to a JSON file
with open('article_links_iep.json', 'w') as file:
    json.dump(article_links, file, indent=4)
    print("Saved article links to article_links_iep.json")



# In[10]:


# Step 2: Fetch and Save Articles
def fetch_and_save_articles_from_links(article_links, output_dir):
    print("Hi")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, link in enumerate(article_links):
        try:
            response = requests.get(link)
            if response.status_code != 200:
                print(f"Failed to retrieve article from {link}. Status code: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)

            # Extract the article title
            title_tag = soup.find('title')
            title = title_tag.get_text() if title_tag else f'article_{i+1}'
            
            # Sanitize the title to create a valid filename
            title = re.sub(r'[\\/*?:"<>|]', "", title)
            filename = os.path.join(output_dir, f"{title}.txt")
            
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(text)
            
            print(f"Saved article {i+1} to {filename}")
        
        except Exception as e:
            print(f"Error processing {link}: {e}")

output_dir = 'articles_text/IEP/'
with open('article_links_iep.json', 'r') as file:
    article_links = json.load(file)

fetch_and_save_articles_from_links(article_links, output_dir)
print("Done")

# In[ ]:





# In[ ]:




