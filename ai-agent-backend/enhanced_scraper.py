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
    
    def scrape_hp(self, query, max_results=10):
        """Scrape HP Store"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://www.hp.com/us-en/search?q={query.replace(' ', '%20')}"
            driver.get(url)
            time.sleep(3) # Wait for JS

            items = driver.find_elements(By.CSS_SELECTOR, '.product-item')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.product-item-link').text
                    price_text = item.find_element(By.CSS_SELECTOR, '.price').text
                    link = item.find_element(By.CSS_SELECTOR, '.product-item-link').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'HP',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"HP scrape error: {e}")
        finally:
            driver.quit()
        return products

    def scrape_dell(self, query, max_results=10):
        """Scrape Dell"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://www.dell.com/en-us/search/{query.replace(' ', '%20')}"
            driver.get(url)
            time.sleep(3)

            items = driver.find_elements(By.CSS_SELECTOR, 'article.stack-system')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'h3.ps-title a').text
                    price_text = item.find_element(By.CSS_SELECTOR, '.ps-dell-price').text
                    link = item.find_element(By.CSS_SELECTOR, 'h3.ps-title a').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'Dell',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"Dell scrape error: {e}")
        finally:
            driver.quit()
        return products

    def scrape_lenovo(self, query, max_results=10):
        """Scrape Lenovo"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://www.lenovo.com/us/en/search?text={query.replace(' ', '%20')}"
            driver.get(url)
            time.sleep(3)

            items = driver.find_elements(By.CSS_SELECTOR, '.product_card')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.product_title').text
                    price_text = item.find_element(By.CSS_SELECTOR, '.final-price').text
                    link = item.find_element(By.CSS_SELECTOR, 'a.product_title_link').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'Lenovo',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"Lenovo scrape error: {e}")
        finally:
            driver.quit()
        return products

    def scrape_acer(self, query, max_results=10):
        """Scrape Acer"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://store.acer.com/en-us/catalogsearch/result/?q={query.replace(' ', '+')}"
            driver.get(url)
            time.sleep(3)

            items = driver.find_elements(By.CSS_SELECTOR, '.product-item')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.product-item-link').text
                    price_text = item.find_element(By.CSS_SELECTOR, '.price').text
                    link = item.find_element(By.CSS_SELECTOR, '.product-item-link').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'Acer',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"Acer scrape error: {e}")
        finally:
            driver.quit()
        return products

    def scrape_microsoft(self, query, max_results=10):
        """Scrape Microsoft Store"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://www.microsoft.com/en-us/search/shop?q={query.replace(' ', '+')}"
            driver.get(url)
            time.sleep(3)

            items = driver.find_elements(By.CSS_SELECTOR, '.m-channel-placement-item')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, 'h3').text
                    price_text = item.find_element(By.CSS_SELECTOR, '[itemprop="price"]').text
                    link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'Microsoft',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"Microsoft scrape error: {e}")
        finally:
            driver.quit()
        return products

    def scrape_apple(self, query, max_results=10):
        """Scrape Apple"""
        products = []
        driver = self.get_driver()
        if not driver: return products

        try:
            url = f"https://www.apple.com/us/search/{query.replace(' ', '+')}?src=globalnav"
            driver.get(url)
            time.sleep(3)

            items = driver.find_elements(By.CSS_SELECTOR, '.rf-serp-product')
            for item in items[:max_results]:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.rf-serp-productname').text
                    price_text = item.find_element(By.CSS_SELECTOR, '.rf-serp-price').text
                    link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                    price = self._parse_price(price_text)
                    if name and price > 0:
                        products.append({
                            'name': name, 'price': price, 'url': link, 'platform': 'Apple',
                            'image': '', 'rating': 0
                        })
                except: continue
        except Exception as e:
            print(f"Apple scrape error: {e}")
        finally:
            driver.quit()
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
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Simplified generic price finding
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for price patterns near "Price" or similar keywords, or specific selectors
            # This is a fallback if selectors fail
            # ... (Existing logic can be kept or simplified)
            
            return 0 # Placeholder for now, specialized logic needed per site
            
        except Exception as e:
            print(f"Error getting price: {e}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def scrape_all_platforms(self, query, max_results_per_platform=10):
        """Scrape multiple platforms concurrently"""
        all_products = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self.scrape_amazon, query, max_results_per_platform): 'Amazon',
                executor.submit(self.scrape_ebay, query, max_results_per_platform): 'eBay',
                executor.submit(self.scrape_walmart, query, max_results_per_platform): 'Walmart',
                executor.submit(self.scrape_hp, query, max_results_per_platform): 'HP',
                executor.submit(self.scrape_dell, query, max_results_per_platform): 'Dell',
                executor.submit(self.scrape_acer, query, max_results_per_platform): 'Acer',
                executor.submit(self.scrape_lenovo, query, max_results_per_platform): 'Lenovo',
                executor.submit(self.scrape_microsoft, query, max_results_per_platform): 'Microsoft',
                executor.submit(self.scrape_apple, query, max_results_per_platform): 'Apple'
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
