import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

base_url = "https://en.wikipedia.org"

exclude_texts = {
    '', 'Main page', 'Article', 'Talk', 'Read', 'View source', 'View history',
    'Help', 'Search', 'Portal', 'Print/export', 'Tools', 'Languages', 'ISBN', 'OCLC'
}

logging.basicConfig(
    format='%(asctime)s %(threadName)s %(levelname)s: %(message)s',
    level=logging.INFO
)

class Link:
    def __init__(self, url, parent=None):
        self.url = url
        self.parent = parent 

    def __repr__(self):
        return f"Link(url={self.url}, parent={self.parent.url if self.parent else None})"

class WikiCrawler:
    def __init__(self):
        self.found_flag = threading.Event()
        self.visited = {}
        self.visited_lock = threading.Lock()
        self.target_link = None
    
    def level_crawler(self, link_obj, target):
        if self.found_flag.is_set():
            return []

        with self.visited_lock:
            if link_obj.url in self.visited:
                logging.info(f"Already visited {link_obj.url}, skipping.")
                return []
            self.visited[link_obj.url] = link_obj

        logging.info(f"Crawling article: {link_obj.url}")

        link_list = []
        try:
            response = requests.get(base_url + link_obj.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            delay = random.uniform(0.5, 2.0)
            logging.info(f"Sleeping for {delay:.2f} seconds")
            time.sleep(delay)

            for link in links:
                if self.found_flag.is_set():
                    break
                    
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and href.startswith("/wiki/") and ':' not in href[6:] and text not in exclude_texts:
                    with self.visited_lock:
                        if href not in self.visited:
                            child_link = Link(url=href, parent=link_obj)
                            link_list.append(child_link)
                            if href == target:
                                self.found_flag.set()
                                self.target_link = child_link
                                logging.info(f"Found target {target} from {link_obj.url}")
                                break
        except Exception as e:
            logging.error(f"Error crawling {link_obj.url}: {e}")

        return link_list

    def reconstruct_path(self, target_link):
        path = []
        current = target_link
        while current:
            path.append(current.url)
            current = current.parent
        path.reverse()
        return path

    def crawl(self, start_url, target_url):
        try:
            start_link = Link(url=start_url, parent=None)
            queue = [start_link]
            max_iterations = 5

            for iteration in range(max_iterations):
                logging.info(f"Queue length: {len(queue)}; Starting crawl iteration {iteration + 1}")
                
                if not queue:
                    logging.info("No more links to crawl. Target not found. Exiting.")
                    break
                
                next_queue = []
                
                with ThreadPoolExecutor() as executor:
                    future_to_link = {
                        executor.submit(self.level_crawler, link, target_url): link 
                        for link in queue
                    }
                    
                    for future in as_completed(future_to_link):
                        if self.found_flag.is_set():
                            break
                        try:
                            result = future.result(timeout=30)
                            if result:
                                next_queue.extend(result)
                        except Exception as e:
                            logging.error(f"Error processing future: {e}")

                if self.found_flag.is_set():
                    logging.info(f"Target {target_url} found! Stopping crawl.")
                    break

                with self.visited_lock:
                    next_queue = [link for link in next_queue if link.url not in self.visited]
                
                queue = next_queue
                logging.info(f"Next queue length after filtering: {len(queue)}")

            if self.found_flag.is_set() and self.target_link:
                path = self.reconstruct_path(self.target_link)
                logging.info(f"Path from start to target:\n" + " -> ".join(path))
                return path
            else:
                logging.info("Target not found.")
                return None
                
        except Exception as e:
            logging.error(f"Unexpected error in crawl: {e}")
            return None
    
def crawl(start_url, target_url):
    crawler = WikiCrawler()
    return crawler.crawl(start_url, target_url)