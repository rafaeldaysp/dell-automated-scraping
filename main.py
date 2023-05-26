from dell import DellBot
import api
import json

def chooseBestCoupon(validCoupons: list, allCoupons: list) -> dict:
    if not validCoupons:
        return None, 0
    
    print(validCoupons, allCoupons)
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
        
    return bestCoupon['id'], bestCouponDiscount

def removeCompetitorCoupons(bestProviderName: str, couponList: list, providerList: list) -> list:
    #newCouponList = []
    competitorsNames = [provider['name'] for provider in providerList if provider['name'] != bestProviderName]
    newCouponList = [coupon for coupon in couponList if not any(competitorName.upper() in coupon['code'].upper() for competitorName in competitorsNames)]
    return newCouponList

def main():
    bot = DellBot()
    allCoupons = api.get_coupons(bot.retailer_id)
    coupons = [coupon for coupon in allCoupons if coupon['available'] and ' + ' not in coupon['code']]
    products = api.get_retailer_products(bot.retailer_id)
    cashback = bot.bestCashbackFinder()
    if cashback:
        coupons = removeCompetitorCoupons(cashback['name'], coupons, bot.cashbackProviders)
        
    for product in products:
        print('produto: ', product['title'], product['html_url'])
        data = {}
        data['price'] = bot.accessCart(product['html_url'])
        data['available'] = True
        validCoupons = []
        for firstCoupon in coupons:
            print(f"testando cupom {firstCoupon['code']}")
            currentPrice = bot.tryCoupon(firstCoupon['code'], data['price'])
            if currentPrice:
                validCoupons.append({"code": firstCoupon['code'], "discount": data['price'] - currentPrice, "available": True, "retailer_id": bot.retailer_id, "discountLabel": firstCoupon['discount'],
                                     "comments": firstCoupon['comments']})
                for secondCoupon in [coupon for coupon in coupons if coupon != firstCoupon]:
                    print(f"testando cupom {secondCoupon['code']}")
                    secondCurrentPrice = bot.tryCoupon(secondCoupon['code'], currentPrice)
                    if secondCurrentPrice:
                        validCoupons.append({"code": f'{firstCoupon["code"]} + {secondCoupon["code"]}', "discount": data['price'] - secondCurrentPrice, "available": True, "retailer_id": bot.retailer_id, "discountLabel": f'{firstCoupon["discount"]} + {secondCoupon["discount"]}',
                                             "comments": "Combinação de cupons disponível na Dell. Obs: não funciona em todos os produtos."})
                        bot.removeCoupon(2)
                bot.removeCoupon(1)
        bestCouponId, bestCouponDiscount = chooseBestCoupon(validCoupons, allCoupons)
        cashbackPercent = 0
        if cashback: cashbackPercent = cashback['value']
        finalPrice = int((data['price'] - bestCouponDiscount)*(1-cashbackPercent/100))
        if finalPrice != data['price'] - bestCouponDiscount:
            r = api.update_product_retailers(product['id'], bot.retailer_id, {"price": finalPrice, "coupon_id": bestCouponId, "cashback": cashback})
            if r.status_code == 200:
                print(f'{product["title"]} -> atualizado com sucesso!')
            else:
                print(r.content)
        bot.removeFromCart()
  
main()