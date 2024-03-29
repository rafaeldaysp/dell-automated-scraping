from dell import DellBot
import api
import json
import time

def chooseBestCoupon(validCoupons: list, allCoupons: list) -> dict:
    if not validCoupons:
        return None, 0, ''
    
    bestCoupon = validCoupons[0]
    for coupon in validCoupons:
        if coupon['discount'] > bestCoupon['discount']:
            bestCoupon = coupon
    bestCouponDiscount = bestCoupon['discount']
    bestCoupon['discount'] = bestCoupon['discountLabel']
    bestCoupon.pop('discountLabel')
   
    couponFinded = False
    for coupon in allCoupons:
        if bestCoupon['code'] == coupon['code']:
            bestCoupon['id'] = coupon['id']
            couponFinded = True
            break
    if not couponFinded:
        r = api.create_coupon(bestCoupon)
        bestCoupon['id'] = json.loads(r.content)['id']
        
    return bestCoupon['id'], bestCouponDiscount, bestCoupon['code']

def removeCompetitorCoupons(bestProviderName: str, couponList: list, providerList: list) -> list:
    competitorsNames = [provider['name'] for provider in providerList if provider['name'] != bestProviderName]
    newCouponList = [coupon for coupon in couponList if not any(competitorName.upper() in coupon['code'].upper() for competitorName in competitorsNames)]
    return newCouponList

def main():
    bot = DellBot()
    allCoupons = api.get_coupons(bot.retailer_id)
    coupons = [coupon for coupon in allCoupons if coupon['available'] and ' + ' not in coupon['code']]
    products = api.get_retailer_products(bot.retailer_id)
    # products = [ product for product in products if 'Mochila Dell EcoLoop Pro 15' in product['title']]
    cashback = bot.bestCashbackFinder()
    
    print(cashback)
    
    if cashback:
        coupons = removeCompetitorCoupons(cashback['name'], coupons, bot.cashbackProviders)
        if cashback['value'] > 2:
            coupons = [coupon for coupon in coupons if 'BENCHPROMOSAW' not in coupon['code']]

    for product in products:
        try:
            print('produto: ', product['title'], product['html_url'])
            data = {}
            price = bot.accessCart(product['html_url'])
            if price == -1:
                if product['available'] == True:
                    r = api.update_product_retailers(product['id'], bot.retailer_id, {"available": False})
                    if r.status_code == 200:
                        print(f'{product["title"]} -> atualizado com sucesso!')
                    else:
                        print(r.content) 
                raise
            data['price'] = price
            data['available'] = True
            validCoupons = []
            for firstCoupon in coupons:
                print(f"testando cupom {firstCoupon['code']}")
                currentPrice = bot.tryCoupon(firstCoupon['code'], data['price'])
                if currentPrice:
                    validCoupons.append({"code": firstCoupon['code'], "discount": data['price'] - currentPrice, "available": True, "retailer_id": bot.retailer_id, "discountLabel": firstCoupon['discount'],
                                        "comments": firstCoupon['comments']})
                    # for secondCoupon in [coupon for coupon in coupons if coupon['code'] != firstCoupon['code']]:
                    #     print(f"testando cupom {secondCoupon['code']}")
                    #     secondCurrentPrice = bot.tryCoupon(secondCoupon['code'], currentPrice)
                    #     print(currentPrice, secondCurrentPrice)
                    #     if secondCurrentPrice:
                    #         validCoupons.append({"code": f'{firstCoupon["code"]} + {secondCoupon["code"]}', "discount": data['price'] - secondCurrentPrice, "available": True, "retailer_id": bot.retailer_id, "discountLabel": f'{firstCoupon["discount"]} + {secondCoupon["discount"]}',
                    #                             "comments": "Combinação de cupons disponível na Dell. Obs: não funciona em todos os produtos."})
                    #         bot.removeCoupon(2)
                    bot.removeCoupon(1)
            bestCouponId, bestCouponDiscount, bestCouponCode = chooseBestCoupon(validCoupons, allCoupons)
            cashbackPercent = 0
            cashbackAplied = ''
            if cashback and cashback != '' and ((data['price'] > 1000000 and cashback['value'] > 1) or cashback['value'] > 4 or cashback['name'] == 'Cuponomia') and 'BENCHPROMOS' not in bestCouponCode: 
                cashbackPercent = cashback['value']
                cashbackAplied = cashback
            finalPrice = int((data['price'] - bestCouponDiscount)*(1-cashbackPercent/100))
            print(finalPrice)
            if 1:#finalPrice != data['price'] - bestCouponDiscount:
                r = api.update_product_retailers(product['id'], bot.retailer_id, {"price": finalPrice, "coupon_id": bestCouponId, "cashback": cashbackAplied, "available": True})
                
                if r.status_code == 200:
                    print(f'{product["title"]} -> atualizado com sucesso!')
                else:
                    print(r.content)
            bot.removeFromCart()
        except Exception as e:
            print("Closing browser and restart app", e)
            bot.closeBrowser()
            bot = DellBot()
    bot.closeBrowser()
  
while True:
    main()
    print("Timeout...")
    time.sleep(3600)