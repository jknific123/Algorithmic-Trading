def pogojBuy2(currCompany_data, avgData):
    # ROE > avg(5 let), D/E < 2, P/B < 1, profitMargin nad 10% in narascajoc trend, age > 10, goodwill > avg, revenue > avg, DCF > cena
    print('Pogoj buy')
    # print(currCompany_data)
    # print()
    # print(avgData)
    # print()

    buy_flags = {}
    buy_flags["ROE"] = True if currCompany_data["ROE"] > avgData["avgROE"] else False  # TODO povprecje ROE za 5 let
    buy_flags["D/E"] = True if currCompany_data["D/E"] < 2 else False
    buy_flags["P/B"] = True if currCompany_data["P/B"] < 2 else False
    buy_flags["profitMargin"] = True if currCompany_data["profitMargin"] > 0.1 else False
    buy_flags["company_age"] = True if currCompany_data["company_age"] > 10 else False
    buy_flags["goodwill"] = True if currCompany_data["goodwill"] > avgData["avgGoodwill"] else False
    # buy_flags["revenue"] = True if currCompany_data["revenue"] > avgData["avgRevenue"] else False
    buy_flags["dcf"] = True if currCompany_data["dcf"] < currCompany_data["price"] else False

    should_buy = True
    napacni_flagi = ''
    for flag in buy_flags:
        if buy_flags[flag] == False:
            should_buy = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(buy_flags[flag]) + ', '

    if not should_buy:
        print(napacni_flagi)

    return should_buy


def pogojSell2(currCompany_data, avgData):
    print('Pogoj sell')
    sell_flags = {}
    sell_flags["ROE"] = True if currCompany_data["ROE"] < avgData["avgROE"] else False  # TODO povprecje ROE za 5 let
    sell_flags["D/E"] = True if currCompany_data["D/E"] > 2 else False
    sell_flags["P/B"] = True if currCompany_data["P/B"] > 2 else False
    sell_flags["profitMargin"] = True if currCompany_data["profitMargin"] < 0.1 else False
    # sell_flags["company_age"] = True if currCompany_data["company_age"] < 10 else False
    # sell_flags["goodwill"] = True if currCompany_data["goodwill"] < avgData["avgGoodwill"] else False
    # sell_flags["revenue"] = True if currCompany_data["revenue"] < avgData["avgRevenue"] else False
    # sell_flags["dcf"] = True if currCompany_data["dcf"] > currCompany_data["price"] else False

    should_sell = True
    napacni_flagi = ''
    for flag in sell_flags:
        if sell_flags[flag] == False:
            should_sell = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(sell_flags[flag]) + ', '

    if not should_sell:
        print(napacni_flagi)

    return should_sell