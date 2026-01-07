from odoo import fields, models, _, api
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin
import base64  # ← FIX: Saknade import
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    # ~ def find_website_allabolag(self, company_name):
        # ~ """ALLABOLAG.SE - korrekt sök-URL för svenska bolag"""
        # ~ if not company_name:
            # ~ _logger.warning("NO COMPANY NAME")
            # ~ return None
        
        # ~ _logger.warning("ALLABOLAG: Searching %s", company_name)
        
        # ~ # RIKTIG Allabolag sök-URL (som du visade)
        # ~ search_query = company_name.lower().replace(' ', '%20')
        # ~ search_url = f"https://www.allabolag.se/bransch-s%C3%B6k?q={search_query}"
        # ~ _logger.warning("ALLABOLAG URL: %s", search_url)
        
        # ~ headers = {
            # ~ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        # ~ }
        
        # ~ try:
            # ~ _logger.warning("ALLABOLAG REQUEST...")
            # ~ r = requests.get(search_url, headers=headers, timeout=10)
            # ~ _logger.warning("ALLABOLAG STATUS: %s", r.status_code)
            # ~ _logger.warning("RESPONSE LENGTH: %s bytes", len(r.text))
            
            # ~ if r.status_code != 200:
                # ~ _logger.error("ALLABOLAG ERROR: %s", r.status_code)
                # ~ return None
                
            # ~ soup = BeautifulSoup(r.text, 'html.parser')
            
            # ~ # LOGGA ALLA LINKAR FÖR DEBUG
            # ~ all_links = soup.find_all('a', href=True)
            # ~ _logger.warning("ALL LINKS FOUND: %s", len(all_links))
            
            # ~ # Hitta företagsresultat (nya selectors)
            # ~ company_links = soup.select('a[href*="/foretag/"], a[href*="/0"], .company-link a, .result a')
            # ~ _logger.warning("COMPANY LINKS: %s", len(company_links))
            
            # ~ for i, link in enumerate(company_links[:5]):
                # ~ href = link.get('href') or ''
                # ~ link_text = link.get_text(strip=True)[:50]
                # ~ _logger.warning("LINK %s: %s | Text: %s", i+1, href, link_text)
                
                # ~ # Extrahera domän från Allabolag eller direkt länk
                # ~ if '/foretag/' in href:
                    # ~ # Allabolag företagsida → domän
                    # ~ company_slug = href.split('/foretag/')[1].split('/')[0].replace('-', '.')
                    # ~ candidate_url = f"https://www.{company_slug}.se"
                # ~ elif 'http' in href and not any(x in href for x in ['allabolag', 'facebook', 'linkedin']):
                    # ~ # Direkt hemsidalänk
                    # ~ candidate_url = href.split('?')[0].split('#')[0]
                # ~ else:
                    # ~ continue
                    
                # ~ _logger.warning("CANDIDATE: %s", candidate_url)
                
                # ~ if self._verify_website(candidate_url):
                    # ~ _logger.warning("SUCCESS: %s VERIFIED", candidate_url)
                    # ~ return candidate_url
                # ~ else:
                    # ~ _logger.warning("VERIFY FAILED: %s", candidate_url)
            
            # ~ _logger.warning("NO VALID WEBSITES FROM ALLABOLAG")
            
            # ~ # FALLBACK: Gissa domän från företagsnamn
            # ~ name_clean = re.sub(r'[^a-z0-9]', '', company_name.lower())
            # ~ fallback = f"https://www.{name_clean}.se"
            # ~ _logger.warning("FALLBACK GUESS: %s", fallback)
            
            # ~ if self._verify_website(fallback):
                # ~ return fallback
                
            # ~ return None
            
        # ~ except Exception as e:
            # ~ _logger.error("ALLABOLAG EXCEPTION: %s", str(e))
            # ~ import traceback
            # ~ _logger.error("TRACEBACK: %s", traceback.format_exc())
            # ~ return None

    # ~ def _verify_website(self, url):
        # ~ """Verifiera hemsida med FULL loggning"""
        # ~ _logger.warning("VERIFY HEAD: %s", url)
        # ~ try:
            # ~ headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            # ~ r = requests.head(url, headers=headers, timeout=7, allow_redirects=True)
            # ~ _logger.warning("VERIFY STATUS: %s", r.status_code)
            # ~ _logger.warning("VERIFY CONTENT-TYPE: %s", r.headers.get('content-type', 'NONE'))
            
            # ~ is_html = 'text/html' in r.headers.get('content-type', '').lower()
            # ~ _logger.warning("IS HTML: %s", is_html)
            
            # ~ result = r.status_code == 200 and is_html
            # ~ _logger.warning("VERIFY RESULT: %s", result)
            # ~ return result
        
        # ~ except Exception as e:
            # ~ _logger.error("VERIFY ERROR: %s", str(e))
            # ~ return False
    
    # ~ def find_website_google_search(self, company_name):
            # ~ """GOOGLE SÖK - hitta hemsida från företagsnamn"""
            # ~ if not company_name:
                # ~ _logger.warning("NO COMPANY NAME")
                # ~ return None
            
            # ~ _logger.warning("START: %s", company_name)
            
            # ~ # Google search query
            # ~ search_query = f'"{company_name}" site:.se OR site:.com "officiell" OR "huvudkontor" OR homepage'
            # ~ _logger.warning("QUERY: %s", search_query)
            
            # ~ google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&num=5"
            # ~ _logger.warning("GOOGLE URL: %s", google_url)
            
            # ~ headers = {
                # ~ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            # ~ }
            
            # ~ try:
                # ~ _logger.warning("SENDING REQUEST...")
                # ~ session = requests.Session()
                # ~ session.headers.update(headers)
                # ~ r = session.get(google_url, timeout=10)
                # ~ _logger.warning("RESPONSE STATUS: %s", r.status_code)
                # ~ _logger.warning("RESPONSE LENGTH: %s bytes", len(r.text))
                
                # ~ if r.status_code != 200:
                    # ~ _logger.error("HTTP ERROR: %s", r.status_code)
                    # ~ return None
                    
                # ~ soup = BeautifulSoup(r.text, 'html.parser')
                # ~ _logger.warning("HTML PARSED")
                
                # ~ # LOGGA ALLA LINKAR
                # ~ all_links = soup.select('div.g a[href]')
                # ~ _logger.warning("FOUND %s Google result links", len(all_links))
                
                # ~ for i, result in enumerate(all_links[:5]):
                    # ~ href = result.get('href') or ''
                    # ~ _logger.warning("LINK %s: %s", i+1, href[:100])
                    
                    # ~ if href and 'http' in href:
                        # ~ # Skippa Google/sociala medier
                        # ~ skip_words = ['google', 'facebook', 'linkedin', 'youtube', 'twitter']
                        # ~ if any(skip in href.lower() for skip in skip_words):
                            # ~ _logger.warning("SKIP: social/tracking (%s)", href[:50])
                            # ~ continue
                        
                        # ~ # Rensa Google params
                        # ~ clean_url = re.sub(r'&gts=.*|&ved=.*|&usg=.*', '', href).split('&')[0]
                        # ~ _logger.warning("CLEAN URL: %s", clean_url)
                        
                        # ~ # Verifiera hemsida
                        # ~ _logger.warning("VERIFYING: %s", clean_url)
                        # ~ if self._verify_website(clean_url):
                            # ~ _logger.warning("SUCCESS: %s VERIFIED OK", clean_url)
                            # ~ return clean_url
                        # ~ else:
                            # ~ _logger.warning("FAILED verification: %s", clean_url)
                
                # ~ _logger.warning("NO VALID WEBSITES FOUND")
                # ~ return None
                
            # ~ except Exception as e:
                # ~ _logger.error("EXCEPTION: %s", str(e))
                # ~ import traceback
                # ~ _logger.error("TRACEBACK: %s", traceback.format_exc())
                # ~ return None

    def find_logo_url(self):
        """Hitta logo URL från website med 15 strategier"""
        if not self.website:
            return None
            
        url = self.website.rstrip('/')
        company_name = self.name or ''
        session = requests.Session()
        
        # Realistiska browser headers (motverkar 403)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        try:
            _logger.warning("Fetching logo from %s", url)
            r = session.get(url, timeout=15, allow_redirects=True)
            
            if r.status_code != 200:
                _logger.warning("HTTP %s for %s", r.status_code, url)
                return None
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 15 strategier för att hitta logo
            strategies = [
                # 1. CSS logo selectors
                lambda: soup.select_one("img[src*='logo'], img[data-src*='logo'], .logo img, #logo img, [class*='logo'] img"),
                
                # 2. Header bilder
                lambda: soup.select_one("header img, .header img, .header-logo img, [class*='header'] img"),
                
                # 3. Open Graph image
                lambda: soup.find("meta", {"property": "og:image"}),
                
                # 4. Bolagsnamn i alt/src
                lambda: next((img.get('src') or img.get('data-src') 
                             for img in soup.find_all("img", limit=50) 
                             if company_name.lower().replace(" ", "") in 
                             (img.get('src','') + img.get('alt','')).lower().replace(" ", "")), None),
                
                # 5. Brand class
                lambda: soup.select_one(".brand img, [class*='brand'] img"),
                
                # 6. Navbar bilder
                lambda: soup.select_one("nav img, .navbar img, .nav img"),
                
                # 7. Favicon
                lambda: urljoin(url, '/favicon.ico'),
                
                # 8. Apple-touch-icon
                lambda: soup.find("link", {"rel": "apple-touch-icon"}),
                
                # 9. Vanliga logo-paths
                lambda: next((urljoin(url, p) for p in 
                             ['/logo.png','/logo.svg','/images/logo.png','/assets/logo.png']), None),
                
                # 10. Meta twitter:image
                lambda: soup.find("meta", {"name": "twitter:image"}),
                
                # 11. Första rimlig header-bild
                lambda: (soup.find("header") or soup.select_one(".header")).find("img") if soup.find("header") else None,
                
                # 12. Site icon
                lambda: soup.find("link", {"rel": "icon"}),
                
                # 13. Största bild (width > 100px)
                lambda: next((img.get('src') for img in soup.find_all("img", limit=30) 
                             if img.get('width', '').isdigit() and int(img.get('width', 0)) > 100), None),
                
                # 14. Första bild i body
                lambda: soup.find("body").find("img") if soup.find("body") else None,
                
                # 15. Fallback - första img
                lambda: soup.find("img", {"src": True})
            ]
            
            for i, strategy in enumerate(strategies, 1):
                result = strategy()
                if result:
                    # Hantera olika resultatyper säkert
                    if hasattr(result, 'get'):
                        src = result.get('src') or result.get('data-src') or result.get('content') or result.get('href')
                    else:
                        src = str(result) if result else None
                    
                    if src and len(src) > 10:
                        logo_url = urljoin(url, src)
                        _logger.warning("Found logo (strategy %d): %s", i, logo_url[:100])
                        return logo_url
            
            _logger.warning("No logo found for %s after 15 strategies", url)
            return None
            
        except Exception as e:
            _logger.error("Logo fetch failed for %s: %s", url, str(e))
            return None

    # ANVÄND I DIN fetch_logo():
    def fetch_logo(self):
        """Hämta hemsida (Allabolag) + logo"""
        for record in self:
            # Steg 1: Allabolag-sök om ingen hemsida
            # ~ if not record.website:
                # ~ website = record.find_website_allabolag(record.name)
                # ~ if website:
                    # ~ record.website = website
                    # ~ _logger.info("Allabolag website for %s: %s", record.name, website)
            
            # Steg 2: Logo om hemsida finns
            if record.website and not record.image_1920:
                logo_url = record.find_logo_url()
                if logo_url:
                    try:
                        r = requests.get(logo_url, timeout=15, stream=True)
                        if r.status_code == 200:
                            image_data = base64.b64encode(r.content).decode('utf-8')
                            record.image_1920 = image_data
                            _logger.info("Logo saved for %s", record.name)
                    except Exception as e:
                        _logger.error("Logo download failed: %s", str(e))



