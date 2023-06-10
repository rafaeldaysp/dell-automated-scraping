from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

SLEEP_TIME = 7

class DellBot():
    def __init__(self) -> None:
        self.retailer_id = 'b43b67ad-a6f4-4525-8a8e-31a829e81c39'
        self.cashbackProviders = [{
                "name": "Cuponomia",
                "affiliatedLink": "https://www.cuponomia.com.br/ref/a8a8ec1cba89",
                "url": "https://www.cuponomia.com.br/desconto/dell",
                "xpath": "/html/body/section[1]/div[1]/div[1]/div/aside/a/span",
            }, {
                "name": "Meliuz",
                "affiliatedLink": "https://www.meliuz.com.br/i/ref_bae7d6a1?ref_source=2",
                "url": "https://www.meliuz.com.br/desconto/cupom-dell",
                "xpath": "/html/body/div[3]/div[4]/button",
            }, 
        ]
        op = webdriver.ChromeOptions()
        op.add_argument("--window-size=1920,1080")
        op.add_argument('--disable-gpu')
        op.add_argument('--no-sandbox')
        op.add_argument('--headless')
        op.add_argument('--disable-dev-shm-usage')
        op.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42")
        #service = Service(ChromeDriverManager().install())
        op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.browser = webdriver.Chrome(executable_path=os.environ.get(CHROMEDRIVER_PATH), options=op)
    
    
    def accessCart(self, url: str) -> int:
        self.browser.get(url)
        time.sleep(SLEEP_TIME)
        try:
            price = int(self.browser.find_element(By.XPATH, '/html/body/main/section[2]/div[1]/div[1]/div[2]/div[2]/span[1]/span[2]').text[3:].replace(',', '').replace('.', ''))
        except Exception as e:
            try:
                price = int(self.browser.find_element(By.XPATH, '//*[@id="cf-body"]/div[4]/div[2]/div[2]/div/div[2]/div').text[3:].replace(',', '').replace('.', ''))
            except:
                raise
        try:
            self.browser.find_element(By.XPATH, '//*[@id="add-to-cart-stack"]/div[2]/button').click()
        except Exception as e:
            try:
                self.browser.find_element(By.XPATH, '//*[@id="cf-body"]/div[4]/div[2]/div[6]/button').click()
            except:
                try:
                    self.browser.find_element(By.XPATH, '//*[@id="cf-body"]/div[4]/div[2]/div[5]/button').click()
                except:
                    try:
                        self.browser.find_element(By.XPATH, '//*[@id="cf-body"]/div[4]/div[2]/div[7]/button').click()
                    except:
                        raise
        time.sleep(SLEEP_TIME)
        self.browser.get('https://www.dell.com/pt-br/cart')
        time.sleep(SLEEP_TIME)
        
        return price
    
    def tryCoupon(self, couponCode: str, lastPrice:int, **kwargs) -> int:
        currentPrice = lastPrice
        priceReturn = 0
        try:
            self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/input').clear()
            self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/input').send_keys(couponCode)
            self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/span/button').click()
            time.sleep(SLEEP_TIME)
            self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/span/button').click()
            time.sleep(SLEEP_TIME)
            currentPrice = int(self.browser.find_element(By.XPATH, '//*[@id="nonpcaas-cart-summary"]/div[3]/ul/li/div[2]/strong').text[2:].replace(',', '').replace('.', '')) 
        except:
            if 'retry' in kwargs:
                print('refreshing page...')
                self.browser.refresh()
            print('Retrying coupon after 30s...')
            time.sleep(30)
            priceReturn = self.tryCoupon(couponCode, lastPrice, retry=True)
        if currentPrice < lastPrice:
            priceReturn = currentPrice
        return priceReturn
    
    def removeFromCart(self):
        try:
            self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[2]/section/div[2]/div/div[2]/div/div/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a').click()
        except:
            try:
                self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[2]/section/div[2]/div/div[2]/div/div/div[1]/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a').click()
            except:
                time.sleep(30)
                self.removeFromCart()
        time.sleep(SLEEP_TIME)
        
    def removeCoupon(self, couponRank, restarted=False):
        try:
            if couponRank == 1:
                self.browser.find_element(By.XPATH, f'/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[1]/div[1]/div[2]/p[2]/small/a[2]').click()
                time.sleep(SLEEP_TIME)
                self.browser.find_element(By.XPATH, f'/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[3]/div/removeappliedcouponmodal/div[3]/button[2]').click()
            else:
                self.browser.find_element(By.XPATH, f'/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[1]/div[2]/div[2]/p[2]/small/a[2]').click()
                time.sleep(SLEEP_TIME)
                self.browser.find_element(By.XPATH, '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[5]/div/removeappliedcouponmodal/div[3]/button[2]').click()
        except Exception as e:
            print('Reiniciando processo de remover cupom.')
            time.sleep(30)
            if restarted: return
            self.removeCoupon(couponRank, restarted=True)
            
        time.sleep(SLEEP_TIME)
    
    def closeBrowser(self):
        self.browser.quit()
        
    def bestCashbackFinder(self):
        cashback = {}
        try:
            for cashbackProvider in self.cashbackProviders:
                self.browser.get(cashbackProvider['url'])
                time.sleep(SLEEP_TIME)
                cashbackFullLabelArray = self.browser.find_element(By.XPATH, cashbackProvider['xpath']).text.split(' ')
                for label in cashbackFullLabelArray:
                    if '%' in label:
                        cashbackProvider['value'] = float(label[:label.find('%')].replace(',', '.'))
                        if not cashback or cashback['value'] < cashbackProvider['value']:
                            cashback = cashbackProvider
        except:
            print('erro na busca de cashbacks')
        return cashback
    
if __name__ == '__main__':
    url = 'https://www.dell.com/pt-br/shop/computadores-all-in-ones-e-workstations/desktop-gamer-alienware-aurora-r15/spd/alienware-aurora-r15-desktop/ar15w20w1'
    k = DellBot()
    price = k.accessCart(url)
    available, price = k.tryCoupon('BEMVINDO150', lastPrice=price)
    print(available, price)
    #k.tryCoupon('SEJANINJA')
    #print(k.couponVerify(url, 'SEJANINJA'))
