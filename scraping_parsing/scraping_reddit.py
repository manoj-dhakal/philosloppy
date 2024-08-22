import praw
import json
import time
import logging

# Set up logging
logging.basicConfig(filename='reddit_dialogues.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the Reddit client
reddit = praw.Reddit(
    client_id='VlnlPn-iEEst0f415pfDvQ',
    client_secret='xYC4hoY5VvoJgzqtdxjpL6Mr2LRSFg',
    user_agent='philosloppy'
)

# List of subreddits to process
subreddits = [
    'philosophy', 'philosophyofscience', 'ethics', 'philpapers', 
    'metaphysics', 'logic', 'epistemology', 'AIethics','continentaltheory','PoliticalPhilosophy','PhilosophyofReligion','atheism','antinatalism'
]

# Initialize an empty list to hold all dialogues
all_conversations = []

# Function to process each subreddit
def process_subreddit(subreddit_name):
    global all_conversations
    subreddit = reddit.subreddit(subreddit_name)
    logging.info(f"Processing subreddit: {subreddit_name}")

    for submission in subreddit.hot(limit=None):  # Process all submissions
        try:
            if submission.num_comments > 10:  # Ensuring it's a discussion
                submission.comments.replace_more(limit=0)
                comments = list(submission.comments.list())
                
                # Create dialogue pairs
                dialogues = []
                for comment in comments:
                    if comment.author:  # Exclude deleted users
                        # Check if this comment is a reply
                        if comment.parent_id.startswith('t1_'):
                            parent_comment = next((c for c in comments if c.id == comment.parent_id[3:]), None)
                            if parent_comment and parent_comment.author and parent_comment.author != comment.author:
                                dialogues.append({
                                    "from": "human",
                                    "value": parent_comment.body
                                })
                                dialogues.append({
                                    "from": "gpt",
                                    "value": comment.body
                                })
                                
                                # Add the conversation to the list
                                all_conversations.append({"conversations": dialogues})
                                dialogues = []  # Reset for the next conversation
                                
                logging.info(f"Processed {len(all_conversations)} conversations from submission {submission.id}")

            time.sleep(1)  # Sleep to avoid overloading the API
        except Exception as e:
            logging.error(f"Error processing submission: {e}")
            time.sleep(10)  # Sleep longer on error

# Process each subreddit
for subreddit_name in subreddits:
    process_subreddit(subreddit_name)

# Save the extracted dialogues
with open('philosophical_dialogues.json', 'w', encoding='utf-8') as f:
    json.dump(all_conversations, f, ensure_ascii=False, indent=4)

logging.info("Data extraction complete. Saved to philosophical_dialogues.json")
