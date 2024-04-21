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
        #print(body_content)
        return body_content.splitlines()
    else:
        # If the request was not successful, print an error message
        print(f"Failed to fetch book content. Status code: {response.status_code}")
        return None

def scrape_conversation(text):
    instructions = []
    outputs = []
    current_instruction = None
    current_output = None

    lines = text.split('\n')
    for line in lines:
        if line.strip() == '':
            continue  # Skip empty lines

        if ":" in line:
            # This line contains a colon, indicating a speaker
            speaker, dialogue = line.split(":", 1)
            if speaker != "SOCRATES":
                # Other characters speaking to Socrates are instructions
                if current_instruction is None:
                    current_instruction = dialogue.strip()
                else:
                    current_instruction += " " + dialogue.strip()
            else:
                # Socrates' dialogue is output
                if current_instruction is not None:
                    instructions.append(current_instruction.strip())
                    current_instruction = None
                if current_output is not None:
                    outputs.append(current_output.strip())
                current_output = dialogue.strip()
        else:
            # This line doesn't contain a colon, it's part of the dialogue
            if current_instruction is not None:
                current_instruction += " " + line.strip()
            if current_output is not None:
                current_output += " " + line.strip()

    # Append the last instruction and output
    if current_instruction is not None:
        instructions.append(current_instruction.strip())
    if current_output is not None:
        outputs.append(current_output.strip())

    return instructions, outputs

# with open('text.txt', 'r', encoding='utf-8') as file:
#     book_content = file.readlines()

url = 'https://www.gutenberg.org/cache/epub/1726/pg1726-images.html'
book_content = fetch_book_content(url)

if book_content == None:
    print("Nothing returned from the website Exiting the program.")
    exit()

# Specify the start and end keywords
start_keyword = 'PERSONS OF THE DIALOGUE:'
end_keyword = '*** END OF THE PROJECT'

# Extract text between the specified start and end points
extracted_text = extract_text(book_content, start_keyword, end_keyword)

# # Print the extracted text
# print(extracted_text)

instructions, outputs = scrape_conversation(extracted_text)

data = {
    "Instructions": instructions,
    "Outputs": outputs
}


df = pd.DataFrame.from_dict(data)
table = pa.Table.from_pandas(df)
pq.write_table(table, 'conversation.parquet')

