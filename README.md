# WebCortex

**WebCortex** is an advanced, production-grade asynchronous web crawler designed to generate high-quality training datasets for AI and large language models (LLMs) such as OpenAI's models or Deepseeks. It leverages modern asynchronous programming with Python's `asyncio` and `aiohttp`, and offers optional spaCy integration for advanced tokenization. With robust error handling, concurrency control, and detailed logging, WebCortex is ideal for researchers, developers, and data scientists looking to harvest clean, high-quality web data.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Asynchronous Crawling:** Uses `asyncio` and `aiohttp` for concurrent HTTP requests, ensuring efficient crawling.
- **Concurrency Control:** Manages parallelism with semaphores to avoid overloading servers.
- **Robust URL Frontier:** An asynchronous queue prevents duplicate URL visits and enforces a maximum page limit.
- **Advanced Tokenization:** Optional integration with spaCy provides high-quality language processing; falls back to regex tokenization if spaCy is not available.
- **Content Extraction:** Utilizes BeautifulSoup to remove scripts, styles, and HTML tags, ensuring clean text extraction.
- **Detailed Reporting:** Logs crawl statistics including start/end times, document count, total tokens processed, and the number of unique terms.
- **Modular Design:** Easily extendable architecture for adding features like sentiment analysis, entity recognition, or distributed crawling.
- **Index Export:** Supports saving a JSON file with a token frequency index for further analysis.

---

## Installation

### Prerequisites

- **Python 3.7+** is required.
- [pip](https://pip.pypa.io/en/stable/) should be installed.

### Dependencies

Install the necessary Python libraries using pip. You can either install them individually or use a `requirements.txt` file.

#### Download Dependencies using `requirements.txt`

```bash
pip install -r requirements.txt
```

### spaCy Model (Optional)

For advanced tokenization, download the English spaCy model:

```bash
python -m spacy download en_core_web_sm
```

If the spaCy model is not installed, WebCortex will automatically fall back to regex-based tokenization.

---

## Usage

WebCortex is executed from the command line. Below is the basic usage pattern:

```bash
python webcortex.py <start_url> [--max_pages MAX_PAGES] [--concurrent_tasks CONCURRENT_TASKS] [--save_index]
```
```bash
python3 webcortex.py <start_url> [--max_pages MAX_PAGES] [--concurrent_tasks CONCURRENT_TASKS] [--save_index]
```

### Example

To crawl a website starting at `http://www.example.com` with a maximum of 500 pages, using 10 concurrent tasks, and saving the token frequency index to disk:

```bash
python webcortex.py http://www.example.com --max_pages 500 --concurrent_tasks 10 --save_index
```

After running, you will see output similar to:

```
>>> 
Enter URL to crawl: http://www.example.com
Start Time: 15:44
Index saved as webcortex_index.json
Documents: 473 Unique Terms: 16056 Tokens: 2751668
End Time: 16:53
>>>
```

---

## Configuration Options

- **`<start_url>`**  
  The starting URL for the crawl (e.g., `http://www.example.com`).

- **`--max_pages MAX_PAGES`**  
  Maximum number of pages to crawl (default is 500).

- **`--concurrent_tasks CONCURRENT_TASKS`**  
  Number of concurrent tasks/workers (default is 10).

- **`--save_index`**  
  Flag to save the token frequency index to a JSON file (`webcortex_index.json`).

---

## Advanced Usage

WebCortex is designed with extensibility in mind. Developers can:

- **Integrate Additional NLP Modules:**  
  Add custom plugins for sentiment analysis, named entity recognition, or topic modeling.

- **Enhance Data Export:**  
  Modify the export functionality to output datasets in formats like CSV or directly to a database.

- **Distributed Crawling:**  
  Expand the architecture to support distributed crawling for very large-scale data collection.

For further customization, refer to the inline comments in the source code and modify functions such as `tokenize()`, `clean_text()`, and `process_url()`.

---

## Contributing

Contributions are welcome! If you’d like to contribute to WebCortex:

1. Fork the repository.
2. Create a feature branch (e.g., `feature/new-nlp-module`).
3. Make your changes.
4. Submit a pull request with a detailed description of your changes.

Please adhere to the project's code style and include tests when applicable.

---

## License


---

## Contact

For questions, suggestions, or support, please open an issue on the GitHub repository or contact the maintainers at [thutatun533@gmail.com] (mailto:thutatun533@gmail.com).

---

