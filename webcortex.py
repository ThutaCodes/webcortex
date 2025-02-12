#!/usr/bin/env python3
"""
WebCortex Advanced Async Crawler: 
A production-grade web crawler that extracts, cleans, and indexes web page text 
to create training datasets for LLMs.

Features:
 - Asynchronous crawling with aiohttp and asyncio
 - Concurrency control via semaphores
 - Optional spaCy integration for advanced tokenization (falls back to regex)
 - Robust error handling and detailed logging
 - Modular design with support for saving token frequency indexes as JSON
 - Configurable crawling limits and concurrency
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import time
import logging
import argparse
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime
from collections import Counter
import logging

# Set the logging level to CRITICAL to hide errors and warnings
logging.basicConfig(level=logging.CRITICAL, format="%(asctime)s [%(levelname)s] %(message)s")

# Attempt to import spaCy for advanced tokenization.
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    USE_SPACY = True
    logging.info("spaCy loaded successfully. Using spaCy for tokenization.")
except Exception as e:
    USE_SPACY = False
    logging.warning("spaCy model not available. Falling back to regex tokenization.")

# Configure logging: time, level, and message.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

class WebCortexAsyncCrawler:
    def __init__(self, start_url, max_pages=500, concurrent_tasks=10):
        self.start_url = start_url
        self.max_pages = max_pages
        self.concurrent_tasks = concurrent_tasks
        self.visited = set()
        self.frontier = asyncio.Queue()
        self.token_counter = Counter()
        self.document_count = 0
        self.token_count = 0
        self.sem = asyncio.Semaphore(concurrent_tasks)
        self.session = None
        self.start_time = None
        self.end_time = None

        # Enqueue the starting URL.
        self.frontier.put_nowait(start_url)

    async def fetch(self, url):
        """Fetch the HTML content for a given URL asynchronously."""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error("Non-200 response for %s: %s", url, response.status)
        except Exception as e:
            logging.error("Error fetching %s: %s", url, e)
        return None

    def clean_text(self, html):
        """Remove scripts, styles, and HTML tags from the HTML to produce clean text."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        return text.strip()

    def tokenize(self, text):
        """Tokenize text using spaCy if available; otherwise, use regex tokenization."""
        if USE_SPACY:
            doc = nlp(text)
            tokens = [token.text.lower() for token in doc if token.is_alpha]
        else:
            tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def extract_links(self, html, base_url):
        """Extract and normalize HTTP/HTTPS links from the HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            absolute_url = urljoin(base_url, href)
            # Only add http/https links.
            if absolute_url.startswith("http"):
                links.add(absolute_url)
        return links

    async def process_url(self, url):
        """Process a single URL: fetch content, extract text and tokens, then enqueue new links."""
        if url in self.visited or len(self.visited) >= self.max_pages:
            return

        logging.info("Processing URL: %s", url)
        html = await self.fetch(url)
        if not html:
            self.visited.add(url)
            return

        self.visited.add(url)
        self.document_count += 1

        # Extract and tokenize text.
        text = self.clean_text(html)
        tokens = self.tokenize(text)
        self.token_count += len(tokens)
        self.token_counter.update(tokens)

        # Extract outbound links and enqueue them if under the max_pages limit.
        links = self.extract_links(html, url)
        for link in links:
            if link not in self.visited and self.frontier.qsize() + len(self.visited) < self.max_pages:
                await self.frontier.put(link)

    async def worker(self):
        """Worker task that continuously processes URLs from the frontier."""
        while True:
            url = await self.frontier.get()
            if url in self.visited or len(self.visited) >= self.max_pages:
                self.frontier.task_done()
                continue
            async with self.sem:
                await self.process_url(url)
            self.frontier.task_done()

    async def crawl(self):
        """Initiate the crawling process with asynchronous workers."""
        self.start_time = time.time()
        logging.info("Starting crawl at %s", datetime.now().strftime("%H:%M:%S"))
        self.session = aiohttp.ClientSession()

        # Launch worker tasks.
        tasks = [asyncio.create_task(self.worker()) for _ in range(self.concurrent_tasks)]
        await self.frontier.join()

        # Cancel all worker tasks.
        for task in tasks:
            task.cancel()

        await self.session.close()
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        logging.info("Crawling completed in %.2f seconds.", elapsed)

        return {
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%H:%M"),
            "end_time": datetime.fromtimestamp(self.end_time).strftime("%H:%M"),
            "documents": self.document_count,
            "tokens": self.token_count,
            "unique_terms": len(self.token_counter)
        }

    def save_index(self, filename="webcortex_index.json"):
        """Save the term frequency index as a JSON file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.token_counter, f, ensure_ascii=False, indent=2)
            logging.info("Index successfully saved to %s", filename)
        except IOError as e:
            logging.error("Error saving index: %s", e)


def main():
    parser = argparse.ArgumentParser(
        description="WebCortex Advanced Async Crawler for AI Training Data"
    )
    parser.add_argument("start_url", help="Starting URL (e.g., https://www.icrc.org/en)")
    parser.add_argument("--max_pages", type=int, default=500, help="Maximum pages to crawl (default: 500)")
    parser.add_argument("--concurrent_tasks", type=int, default=10, help="Concurrent tasks (default: 10)")
    parser.add_argument("--save_index", action="store_true", help="Save token frequency index as JSON")
    args = parser.parse_args()

    # Validate the provided URL.
    parsed_url = urlparse(args.start_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logging.error("Invalid URL provided: %s", args.start_url)
        return

    crawler = WebCortexAsyncCrawler(args.start_url, args.max_pages, args.concurrent_tasks)

    try:
        loop = asyncio.get_event_loop()
        stats = loop.run_until_complete(crawler.crawl())
    except KeyboardInterrupt:
        logging.info("Crawl interrupted by user.")
        return

    # Output the crawl summary.
    print("\n>>>")
    print("Enter URL to crawl:", args.start_url)
    print("Start Time:", stats["start_time"])
    if args.save_index:
        crawler.save_index()
        print("Index saved as webcortex_index.json")
    print("Documents:", stats["documents"],
          "Unique Terms:", stats["unique_terms"],
          "Tokens:", stats["tokens"])
    print("End Time:", stats["end_time"])
    print(">>>")

if __name__ == "__main__":
    main()
