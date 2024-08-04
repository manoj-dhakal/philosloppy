# PhiloSloppy 🌟

Welcome to PhiloSloppy, where we delve into philosophical conversations with finesse and fun! 🤔💬

## Overview

PhiloSloppy is a charming project dedicated to refining cutting-edge LLM models for engaging philosophical dialogues. Our journey involves three delightful phases:

1) **Data Collection:** 📚 Dive into the enchanting world of Plato's dialogues for the "shockrates" model, and explore texts from the Stanford Encyclopedia of Philosophy and the Internet Encyclopedia of Philosophy for the "philoslopper" model. 🏛️✨ Our datasets, stored in Hugging Face, feature meticulously converted texts into .parquet format, ready for exploration.

2) **Fine Tuning:** ✨ Embark on a quest to fine-tune the "unsloth/llama-3-8b-Instruct-bnb-4bit" model using Llama 3 and Unsloth. 🚀 Witness our models blossom into conversational virtuosos, ready for philosophical ponderings.

3) **Deployment:** 🌐 Watch as our refined models gracefully take their places on the digital stage! Currently accessible on local machines using Ollama and soon accessible via a serverless API, our models eagerly await to engage in spirited discussions, easily accessible with simple commands.

## Usage

Now, you can access our models directly from Ollama! 🎉

1. **Start the Ollama server:**
   ```bash
   ollama serve
   ```
2.	Run the Socrates model (“shockrates”):
 ```bash
   ollama run philosloppy/shockrates
   ```
3.	Run the general philosophy model (“philoslopper”):
```bash
ollama run philosloppy/philoslopper
    ```
5.	

Credits

PhiloSloppy is brought to you with love by two passionate philosophy and AI lovers, Ashok Timsina (https://github.com/timsinashok) and Manoj Dhakal (https://github.com/manoj-dhakal. Join us on this whimsical journey as we unravel the mysteries of philosophy, one conversation at a time! 🎩🌹

Let’s Chat!

Got questions, suggestions, or just want to say hello? Reach out to us! We’re always excited to connect with fellow thinkers and dreamers. 💌

Visit our Ollama profile: [PhiloSloppy on Ollama](https://ollama.com/philosloppy)

Happy philosophizing! 🌟📜
