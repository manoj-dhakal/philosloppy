import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup

def extract_text(book_content, start_keyword, end_keyword):
    start_found = False
    end_found = False

    extracted_text = []
    for line in book_content:
        if start_keyword in line:
            start_found = True

        if end_keyword in line:
            end_found = True
            break  
        if start_found:
            extracted_text.append(line.strip())

    extracted_text = ' \n'.join(extracted_text)

    return extracted_text

def fetch_book_content(book_url):
    response = requests.get(book_url)
    
    if response.status_code == 200:
        html_content = response.text
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the body tag and extract its text
        body_content = soup.get_text(separator='\n', strip=True)
        return body_content.splitlines()
    else:
        # If the request was not successful, print an error message
        print(f"Failed to fetch book content. Status code: {response.status_code}")
        return None

def scrape_conversation(text):
    conversation_pairs = []
    current_speaker = None
    current_message = []

    lines = text.split('\n')
    for line in lines:
        if line.strip() == '':
            continue  # Skip empty lines

        if ":" in line:
            # This line contains a colon, indicating a speaker
            speaker, dialogue = line.split(":", 1)
            if speaker == "SOCRATES":
                if current_speaker == "human" and current_message:
                    conversation_pairs.append({"from": "human", "value": " ".join(current_message).strip()})
                if current_speaker == "gpt" and current_message:
                    conversation_pairs.append({"from": "gpt", "value": " ".join(current_message).strip()})
                current_speaker = "gpt"
                current_message = [dialogue.strip()]
            else:
                if current_speaker == "gpt" and current_message:
                    conversation_pairs.append({"from": "gpt", "value": " ".join(current_message).strip()})
                current_speaker = "human"
                current_message = [dialogue.strip()]
        else:
            # This line doesn't contain a colon, it's part of the dialogue
            if current_message:
                current_message.append(line.strip())

    # Append the last message
    if current_speaker == "human" and current_message:
        conversation_pairs.append({"from": "human", "value": " ".join(current_message).strip()})
    elif current_speaker == "gpt" and current_message:
        conversation_pairs.append({"from": "gpt", "value": " ".join(current_message).strip()})

    # Combine adjacent human and gpt messages into one data point
    combined_conversations = []
    i = 0
    while i < len(conversation_pairs) - 1:
        if conversation_pairs[i]['from'] == "human" and conversation_pairs[i + 1]['from'] == "gpt":
            combined_conversations.append([
                {"from": "human", "value": conversation_pairs[i]['value']},
                {"from": "gpt", "value": conversation_pairs[i + 1]['value']}
            ])
            i += 2
        else:
            i += 1  # Skip mismatched pairs

    return combined_conversations

urls = {'Theaetetus':'https://www.gutenberg.org/cache/epub/1726/pg1726-images.html', 
       'PHAEDRUS': 'https://www.gutenberg.org/cache/epub/1636/pg1636-images.html',
       'GORGIAS': 'https://www.gutenberg.org/cache/epub/1672/pg1672-images.html',
       'LAWS': 'https://www.gutenberg.org/cache/epub/1750/pg1750-images.html',
       'PHAEDO': 'https://www.gutenberg.org/cache/epub/1658/pg1658-images.html',
       'TIMAEUS': 'https://www.gutenberg.org/cache/epub/1572/pg1572-images.html',
       'EUTHYPHRO': 'https://www.gutenberg.org/cache/epub/1642/pg1642-images.html',
       'MENO': 'https://gutenberg.org/cache/epub/1643/pg1643-images.html',
       'ION': 'https://www.gutenberg.org/cache/epub/1635/pg1635-images.html',
       # New addition
       'CRATYLUS': 'https://www.gutenberg.org/cache/epub/1616/pg1616-images.html',
       'MENEXENUS': 'https://www.gutenberg.org/cache/epub/1682/pg1682-images.html',
       'PHILEBUS': 'https://www.gutenberg.org/cache/epub/1744/pg1744-images.html',
       'EUTHYDEMUS': 'https://www.gutenberg.org/cache/epub/1598/pg1598-images.html',
       'LACHES': 'https://www.gutenberg.org/cache/epub/1584/pg1584-images.html',
       }

if __name__ == "__main__":
    data_rows = []

    for name, link in urls.items():
        print("Reading book:", name)
        book_content = fetch_book_content(link)
        print("Extracting conversation from book...")
        
        if book_content == None:
            print("Nothing returned from the website. Exiting the program.")
            exit()

        # Specify the start and end keywords
        start_keyword = 'PERSONS OF THE DIALOGUE:'
        end_keyword = '*** END OF THE PROJECT'

        # Extract text between the specified start and end points
        extracted_text = extract_text(book_content, start_keyword, end_keyword)

        conversations = scrape_conversation(extracted_text)

        # Add each conversation pair to data_rows
        for conv in conversations:
            data_rows.append({"conversations": conv})

    # Create DataFrame from data_rows
    df = pd.DataFrame(data_rows)

    # Convert to Parquet file
    table = pa.Table.from_pandas(df)
    pq.write_table(table, 'conversation.parquet')
