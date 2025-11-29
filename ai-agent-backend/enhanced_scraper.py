import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re

class EnhancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_driver(self, headless=True):
        """Initialize Chrome driver with optimal settings"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Error creating WebDriver: {e}")
            return None
    
    def rate_limit(self, min_delay=1, max_delay=3):
        """Add random delay between requests"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def _parse_price(self, text):
        """Helper to parse price string"""
        if not text:
            return 0
        try:
            # Remove currency symbols and cleanup
            clean_text = re.sub(r'[^\d.,]', '', text)
            # Find the first valid number
            match = re.search(r'(\d+[\.,]?\d*)', clean_text)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
        except:
            pass
        return 0

    def scrape_amazon(self, query, max_results=10):
        """Enhanced Amazon scraping with pagination"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            print("Failed to initialize WebDriver for Amazon")
            return products
        
        try:
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]'))
            )
            
            product_elements = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
            
            for i, element in enumerate(product_elements[:max_results]):
                try:
                    # Name
                    name_elem = None
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, 'h2 span')
                    except:
                        pass
                    
                    if not name_elem:
                        continue
                    
                    name = name_elem.text.strip()
                    
                    # Price - Improved logic
                    price = 0
                    price_text = ""
                    
                    # Try getting price from visible text or hidden text
                    try:
                        # Strategy 1: Look for whole and fraction parts
                        whole = element.find_element(By.CSS_SELECTOR, '.a-price-whole').text
                        fraction = element.find_element(By.CSS_SELECTOR, '.a-price-fraction').text
                        price_text = f"{whole}.{fraction}"
                    except:
                        # Strategy 2: Look for offscreen price
                        try:
                            price_elem = element.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen')
                            price_text = price_elem.get_attribute("textContent")
                        except:
                            pass

                    price = self._parse_price(price_text)
                    
                    # Link
                    link = ""
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
                        link = link_elem.get_attribute('href')
                    except:
                        pass
                    
                    # Image
                    image = ""
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, 'img.s-image')
                        image = img_elem.get_attribute('src')
                    except:
                        pass

                    if name and price > 0:
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': 0, # Simplified
                            'image': image,
                            'url': link,
                            'platform': 'Amazon'
                        })

                except Exception as e:
                    print(f"Error parsing Amazon product {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Amazon: {e}")
        finally:
            driver.quit()
            
        self.rate_limit()
        return products
    
    def scrape_ebay(self, query, max_results=10):
        """Enhanced eBay scraping"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            print("Failed to initialize WebDriver for eBay")
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
                    
                    price = self._parse_price(price_text)
                    
                    if price > 0 and 'Shop on eBay' not in name:
                        product = {
                            'name': name,
                            'price': price,
                            'url': link,
                            'platform': 'eBay',
                            'rating': 0,
                            'image': ''
                        }
                        products.append(product)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping eBay: {e}")
        finally:
            driver.quit()
            
        self.rate_limit()
        return products
    
    def scrape_walmart(self, query, max_results=10):
        """Enhanced Walmart scraping"""
        products = []
        driver = self.get_driver()
        
        if not driver:
            print("Failed to initialize WebDriver for Walmart")
            return products
        
        try:
            search_url = f"https://www.walmart.com/search?q={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for products to load
            time.sleep(5)
            
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
                    price_text = ""
                    try:
                        price_elem = element.find_element(By.CSS_SELECTOR, '[data-automation-id="product-price"]')
                        price_text = price_elem.text
                    except: pass
                    
                    price = self._parse_price(price_text)
                    
                    # Link
                    link = ""
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                        link = link_elem.get_attribute('href')
                    except: pass
                    
                    if name and price > 0:
                        product = {
                            'name': name,
                            'price': price,
                            'url': link,
                            'platform': 'Walmart',
                            'rating': 0,
                            'image': ''
                        }
                        products.append(product)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping Walmart: {e}")
        finally:
            driver.quit()
            
        self.rate_limit()
        return products
    
    def get_current_price(self, product_url):
        """Get current price for a specific product URL"""
        try:
            driver = self.get_driver()
            driver.get(product_url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try different price selectors based on the URL
            price_selectors = []

            if 'amazon' in product_url.lower():
                price_selectors = [
                    '.a-price-whole',
                    '.a-offscreen',
                    '.a-price.a-text-price.a-size-medium.apexPriceToPay',
                    '.a-price-range',
                    'span.a-price',
                    '[data-a-size="xl"] .a-offscreen',
                    '.a-price .a-offscreen'
                ]
            elif 'ebay' in product_url.lower():
                price_selectors = [
                    '.price .amt',
                    '.notranslate',
                    '.u-flL.condText',
                    '.amt.vi-price .notranslate',
                    '.display-price',
                    '.vim x-price-primary'
                ]
            elif 'walmart' in product_url.lower():
                price_selectors = [
                    '[itemprop="price"]',
                    '[data-testid="price"]',
                    '.price-group',
                    '.price-current'
                ]
            else:
                # Generic selectors for other sites
                price_selectors = [
                    '.price',
                    '[class*="price"]',
                    '[data-price]',
                    '[itemprop="price"]'
                ]
            
            # Try each selector
            for selector in price_selectors:
                try:
                    price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if price_elem:
                        price_text = price_elem.get_attribute('content') or price_elem.text or price_elem.get_attribute('textContent')
                        price = self._parse_price(price_text)
                        if price > 0:
                            return price
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error getting price for {product_url}: {e}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()
    
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
                    print(f"Scraped {len(products)} products from {platform}")
                except Exception as e:
                    print(f"Error scraping {platform}: {e}")
        
        return all_products
