from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import api

SLEEP_TIME = 7

class DellBot():
    def __init__(self) -> None:
        self.retailer_id = 'b43b67ad-a6f4-4525-8a8e-31a829e81c39'
        self.cashbackProviders = [
            {
                "name": "Meliuz",
                "affiliatedLink": "https://www.meliuz.com.br/i/ref_bae7d6a1?ref_source=2",
                "url": "https://www.meliuz.com.br/desconto/cupom-acer",
                "xpath": "/html/body/div[3]/div[4]/button",
                "xpath2": "/html/body/div[3]/div[4]/button",
            },{
            
                "name": "Cuponomia",
                "affiliatedLink": "https://www.cuponomia.com.br/ref/a8a8ec1cba89",
                "url": "https://www.cuponomia.com.br/desconto/dell",
                "xpath": "/html/body/section[2]/div[1]/div[1]/div/aside/a/span",
                "xpath2": "/html/body/section[1]/div[1]/div[1]/div/aside/a/span"
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
        op.add_argument('--disable-blink-features=AutomationControlled')
        op.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42")
        service = Service(ChromeDriverManager().install())
        #op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.browser = webdriver.Chrome(service=service, options=op)
    
    
    def accessCart(self, url: str) -> int:
        self.browser.get(url)
        time.sleep(SLEEP_TIME)
        
        
        price_xpath_list = [
            '/html/body/main/section[2]/div[1]/div[1]/div[2]/div[2]/span[1]/span[2]',
            '//*[@id="cf-body"]/div[4]/div[2]/div[2]/div/div[2]/div',
            '/html/body/div[4]/div[1]/div[5]/div/div/article/section/div[2]/div[1]/div[1]',
            '//*[@id="460-bczs"]/section/div[2]/div[1]/div[1]'
        ]
        element_located = False
        price = 0
        for xpath in price_xpath_list:
            try:
                price = int(self.browser.find_element(By.XPATH, xpath).text[3:].replace(',', '').replace('.', ''))
                element_located = True
                break
            except:
                pass
        if not element_located:
            raise
        print(price)
        # try:
        #     price = int(self.browser.find_element(By.XPATH, '/html/body/main/section[2]/div[1]/div[1]/div[2]/div[2]/span[1]/span[2]').text[3:].replace(',', '').replace('.', ''))
        # except Exception as e:
        #     try:
        #         price = int(self.browser.find_element(By.XPATH, '//*[@id="cf-body"]/div[4]/div[2]/div[2]/div/div[2]/div').text[3:].replace(',', '').replace('.', ''))
        #     except:
        #         raise
        button_xpath_list = [
            '//*[@id="add-to-cart-stack"]/div[2]/button',
            '//*[@id="cf-body"]/div[4]/div[2]/div[6]/button',
            '//*[@id="cf-body"]/div[4]/div[2]/div[5]/button',
            '//*[@id="cf-body"]/div[4]/div[2]/div[7]/button',
            '//*[@id="460-bczs"]/section/div[5]/div/a'
            
        ]
        
        element_located = False
        for xpath in button_xpath_list:
            try:
                self.browser.find_element(By.XPATH, xpath).click()
                element_located = True
            except:
                pass
        if not element_located:
            print("Não foi possível adicionar ao carrinho.")
            return -1
        
        time.sleep(SLEEP_TIME)
        self.browser.get('https://www.dell.com/pt-br/cart')
        time.sleep(SLEEP_TIME)
        
        return price
    
    def tryCoupon(self, couponCode: str, lastPrice:int, **kwargs) -> int:
        currentPrice = lastPrice
        priceReturn = 0
        
        try:
            self.browser.find_element(By.XPATH, '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/input').clear()
            self.browser.find_element(By.XPATH, '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/input').send_keys(couponCode)
            self.browser.find_element(By.XPATH, '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/span/button').click()
            time.sleep(SLEEP_TIME)
            self.browser.find_element(By.XPATH, '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/applycoupon/div[1]/div/div/div/span/button').click()
            time.sleep(SLEEP_TIME)
            currentPrice = int(self.browser.find_element(By.XPATH, '//*[@id="nonpcaas-cart-summary"]/div[3]/ul/li/div[2]/strong').text[2:].replace(',', '').replace('.', '')) 
        except:
            if 'double_retry' in kwargs:
                raise
            elif 'retry' in kwargs:
                print('refreshing page...')
                print(kwargs)
                self.browser.refresh()
                time.sleep(SLEEP_TIME)
                priceReturn = self.tryCoupon(couponCode, lastPrice, double_retry = True)
                time.sleep(SLEEP_TIME)
            else: 
                print('Retrying coupon after 30s...')
                time.sleep(30)
                priceReturn = self.tryCoupon(couponCode, lastPrice, retry = True)
        if currentPrice < lastPrice:
            priceReturn = currentPrice
        return priceReturn
    
    def removeFromCart(self):

        xpath_list = [
            '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[1]/section/div[2]/div/div[2]/div/div/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a',
            '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[2]/section/div[2]/div/div[2]/div/div/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a',
            '/html/body/div[4]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[2]/section/div[2]/div/div[2]/div/div/div[1]/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a',
            '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[1]/section/div[2]/div/div[2]/div/div/div[1]/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a',
            '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/section/div/div/div/div[1]/section/div[2]/div/div[2]/div/div/div[1]/div[4]/div[1]/div[3]/div[2]/div[1]/div/item-quantity/div/div/a'
        ]
        
        removed = False
        for xpath in xpath_list:
            try:
                self.browser.find_element(By.XPATH, xpath).click()
                removed = True
                break
            except:
                pass
                
        if not removed:
            time.sleep(30)
            self.removeFromCart()
        time.sleep(SLEEP_TIME)
        
    def removeCoupon(self, couponRank, restarted=False):
        try:
            if couponRank == 1:
                self.browser.find_element(By.XPATH, f'/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[1]/div/div[2]/p[2]/small/a[2]').click()
                time.sleep(SLEEP_TIME)
                self.browser.find_element(By.XPATH, f'/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[3]/div/removeappliedcouponmodal/div[3]/button[2]').click()
            else:
                self.browser.find_element(By.XPATH, f'/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[1]/div[2]/div[2]/p[2]/small/a[2]').click()
                time.sleep(SLEEP_TIME)
                self.browser.find_element(By.XPATH, '/html/body/div[3]/div/section/div/div/div[1]/div[1]/div[2]/div[2]/div[5]/aside[1]/div/div/desktopappliedcouponmessagewrapper/div[5]/div/removeappliedcouponmodal/div[3]/button[2]').click()
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
        # try:
        for cashbackProvider in self.cashbackProviders:
            self.browser.get(cashbackProvider['url'])
            time.sleep(SLEEP_TIME)
            cashbackFullLabelArray = []
            try: cashbackFullLabelArray = self.browser.find_element(By.XPATH, cashbackProvider['xpath']).text.split(' ')
            except: 
                try: cashbackFullLabelArray = self.browser.find_element(By.XPATH, cashbackProvider['xpath2']).text.split(' ')
                except: pass
            for label in cashbackFullLabelArray:
                if '%' in label:
                    cashbackProvider['value'] = float(label[:label.find('%')].replace(',', '.'))

                    ## gambiarra
                    retailer = 'Dell'
                    if cashbackProvider['name'] == 'Meliuz' and 'acer' in cashbackProvider['url']:
                        coupon_id = 'a4e0d2ba-b3ae-41f0-ba3f-fe63a9aefe94'
                        data = { "discount": str(cashbackProvider['value']) + '%'}
                        r = api.update_coupon(coupon_id, data)
                        retailer = 'Acer'
                    ##
                    
                    if (not cashback or cashback['value'] < cashbackProvider['value']) and retailer == 'Dell':
                        cashback = cashbackProvider
        # except:
        #     print('erro na busca de cashbacks')
        return cashback
    
if __name__ == '__main__':
    url = 'https://www.dell.com/pt-br/shop/mochila-dell-gaming/apd/460-bczs/acess%C3%B3rios-para-jogos?cjevent=b00fbf172b2e11ee83f2ff3f0a82b832&publisherid=6608840&publisher=&aff=Ishii+Producoes&affid=6608840&aff_webid=100921865&aff_user_id=&cjdata=MXxOfDB8WXww&gacd=9657105-29789130-5750457-364944948-190032919&dgc=af&VEN1=100921865&dclid=CMyAzv3gqoADFfdD3QIdGNsPxg'
    k = DellBot()
    price = k.accessCart(url)
    available, price = k.tryCoupon('BEMVINDO150', lastPrice=price)
    print(available, price)
    #k.tryCoupon('SEJANINJA')
    #print(k.couponVerify(url, 'SEJANINJA'))
