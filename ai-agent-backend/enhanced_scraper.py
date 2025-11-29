import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
    def get_driver(self, headless=True):
        """Initialize Chrome driver with optimal settings"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Use webdriver_manager to automatically handle driver installation
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Stealth settings
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"Error creating WebDriver: {e}")
            return None
    
    def rate_limit(self, min_delay=1, max_delay=3):
        """Add random delay between requests"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def _scrape_fallback(self, url, platform):
        """Fallback scraping using requests if Selenium fails"""
        products = []
        try:
            logger.info(f"Attempting fallback scrape for {platform} via requests")
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return products

            soup = BeautifulSoup(response.text, 'html.parser')

            if platform == 'Amazon':
                items = soup.select('[data-component-type="s-search-result"]')
                for item in items[:5]:
                    title = item.select_one('h2 span')
                    price_whole = item.select_one('.a-price-whole')
                    price_frac = item.select_one('.a-price-fraction')
                    link = item.select_one('h2 a')

                    if title and price_whole:
                        name = title.text.strip()
                        price = float(price_whole.text.replace(',', '') + ('.' + price_frac.text if price_frac else ''))
                        url = 'https://amazon.com' + link.get('href') if link else ''
                        products.append({'name': name, 'price': price, 'url': url, 'platform': platform, 'rating': 0, 'image': ''})

        except Exception as e:
            logger.error(f"Fallback scrape failed: {e}")

        return products

    def scrape_amazon(self, query, max_results=10):
        """Enhanced Amazon scraping with pagination"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            logger.warning("WebDriver failed, switching to fallback for Amazon")
            return self._scrape_fallback(f"https://www.amazon.com/s?k={query.replace(' ', '+')}", 'Amazon')
        
        try:
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for products to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]'))
                )
            except:
                logger.warning("Timeout waiting for Amazon results")
            
            product_elements = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
            
            if not product_elements:
                logger.warning("No Amazon products found with Selenium")

            for i, element in enumerate(product_elements[:max_results]):
                try:
                    # Name
                    name_elem = None
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, 'h2 span')
                    except: pass
                    
                    if not name_elem: continue
                    name = name_elem.text.strip()
                    
                    # Price
                    price = 0
                    try:
                        # Try standard price structure
                        price_elem = element.find_element(By.CSS_SELECTOR, '.a-price')
                        # Use textContent to get hidden text
                        price_text = price_elem.get_attribute('textContent')
                        # Extract first valid price number
                        import re
                        match = re.search(r'\$?(\d{1,3}(?:,\d{3})*\.?\d{0,2})', price_text)
                        if match:
                            price = float(match.group(1).replace(',', ''))
                    except:
                        pass
                    
                    # Link
                    link = ""
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
                        link = link_elem.get_attribute('href')
                    except: pass

                    if name and price > 0:
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': 0,
                            'image': '',
                            'url': link,
                            'platform': 'Amazon'
                        })

                except Exception as e:
                    logger.error(f"Error parsing Amazon product {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
        finally:
            if driver:
                driver.quit()
            
        self.rate_limit()
        return products
    
    def scrape_ebay(self, query, max_results=10):
        """Enhanced eBay scraping"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            return products
        
        try:
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
            driver.get(search_url)
            
            product_elements = driver.find_elements(By.CSS_SELECTOR, '.s-item')[:max_results]
            
            for element in product_elements:
                try:
                    name = element.find_element(By.CSS_SELECTOR, '.s-item__title').text
                    price_text = element.find_element(By.CSS_SELECTOR, '.s-item__price').text
                    link = element.find_element(By.CSS_SELECTOR, '.s-item__link').get_attribute('href')
                    
                    # Extract price
                    price_cleaned = price_text.replace('$', '').replace(',', '').split()[0]
                    try:
                        price = float(price_cleaned)
                    except:
                        price = 0
                    
                    if price > 0 and 'Shop on eBay' not in name:
                        products.append({
                            'name': name,
                            'price': price,
                            'url': link,
                            'platform': 'eBay',
                            'rating': 0,
                            'image': ''
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping eBay: {e}")
        finally:
            if driver:
                driver.quit()
            
        self.rate_limit()
        return products
    
    def scrape_walmart(self, query, max_results=10):
        """Enhanced Walmart scraping"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            return products
        
        try:
            search_url = f"https://www.walmart.com/search?q={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for products to load
            time.sleep(3)
            
            # Try multiple selectors for product containers
            product_elements = []
            container_selectors = [
                '[data-testid="item"]',
                '[data-automation-id="product-tile"]',
                '.search-result-gridview-item',
                '.Grid-col'
            ]
            
            for selector in container_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        product_elements = elements[:max_results]
                        break
                except:
                    continue
            
            for i, element in enumerate(product_elements):
                try:
                    # Name
                    name = ""
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, '[data-automation-id="product-title"]')
                        name = name_elem.text.strip()
                    except: pass
                    
                    if not name: continue
                    
                    # Price
                    price = 0
                    try:
                        price_elem = element.find_element(By.CSS_SELECTOR, '[data-automation-id="product-price"]')
                        price_text = price_elem.text
                        import re
                        match = re.search(r'\$?(\d+\.?\d*)', price_text.replace(',', ''))
                        if match:
                            price = float(match.group(1))
                    except: pass
                    
                    # Link
                    link = ""
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                        link = link_elem.get_attribute('href')
                    except: pass
                    
                    if name and price > 0:
                        products.append({
                            'name': name,
                            'price': price,
                            'url': link,
                            'platform': 'Walmart',
                            'rating': 0,
                            'image': ''
                        })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Walmart: {e}")
        finally:
            if driver:
                driver.quit()
            
        self.rate_limit()
        return products
    
    def get_current_price(self, product_url):
        """Get current price for a specific product URL"""
        return None # Simplified for now
    
    def scrape_all_platforms(self, query, max_results_per_platform=10):
        """Scrape multiple platforms concurrently"""
        all_products = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.scrape_amazon, query, max_results_per_platform): 'Amazon',
                executor.submit(self.scrape_ebay, query, max_results_per_platform): 'eBay',
                executor.submit(self.scrape_walmart, query, max_results_per_platform): 'Walmart'
            }
            
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    products = future.result()
                    all_products.extend(products)
                    logger.info(f"Scraped {len(products)} products from {platform}")
                except Exception as e:
                    logger.error(f"Error scraping {platform}: {e}")
        
        return all_products
