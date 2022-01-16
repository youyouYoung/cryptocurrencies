 
'''backtest
start: 2021-03-01 00:00:00
end: 2021-03-31 00:00:00
period: 1m
basePeriod: 1m
exchanges: [{"eid":"Futures_Binance","currency":"BCH_USDT"}]
'''
import random
from enum import Enum

class PositionChangeType(Enum):
    Init = 1
    TirckerChange = 2
    StopProfit = 3
    StopLoss = 4

unit = 0.01
profit = 0
initAccount = 0


# 打印收益
def logProfit(ticker):
    global initAccount
    account = exchange.GetAccount()
    netNow = account.Balance + account.FrozenBalance + ((account.Stocks + account.FrozenStocks) * ticker.Buy);
    netInit = initAccount.Balance + initAccount.FrozenBalance + ((initAccount.Stocks + initAccount.FrozenStocks) * ticker.Buy);
    LogProfit(netNow - netInit);

# 买单
def buyUnit(ticker, positions, positionChangeType):

    exchange.SetDirection("buy")
    exchange.Buy(round(ticker['Last']*(1+0.01)), 0.01)

    # 如果是止盈后开仓 判断另一边的仓位 如果仓位过大 可以按比例开高开一些
    if positionChangeType == PositionChangeType.StopProfit:
        for p in positions:
            if p.Type == PD_SHORT:
                if p['Amount']/0.01 > 50:
                    exchange.Buy(round(ticker['Last']*(1+0.01)), p['Amount']/10)
    # # 打印收益
    logProfit(ticker)
            
# 卖单
def sellUnit(ticker, positions, positionChangeType):
    exchange.SetDirection("sell")
    exchange.Sell(round(ticker['Last']*(1-0.01)), 0.01)

     # 如果是止盈后开仓 判断另一边的仓位 如果仓位过大 可以按比例开高开一些
    if positionChangeType == PositionChangeType.StopProfit:
        for p in positions:
            if p.Type == PD_LONG:
                if p['Amount']/0.01 > 50:
                    exchange.Sell(round(ticker['Last']*(1-0.01)), p['Amount']/10)
    # 打印收益
    logProfit(ticker)
   
# 初始化开仓 同时开多 开空
def initPosition(ticker,positions):
    # positions = exchange.GetPosition()
    longNum = 0
    shortNum = 0
    for p in positions:
        if p.Type == PD_LONG:
            longNum = 1
        elif p.Type == PD_SHORT:
            shortNum = 1
    if longNum == 0:
        buyUnit(ticker, positions, PositionChangeType.Init)
    if shortNum == 0:
        sellUnit(ticker, positions, PositionChangeType.Init)

stopLossDict = {}

def disposePostion(ticker, positions):
    global stopLossDict
    global stopLossRest
    global profit
    
    for p in positions:
        yieldRate = p['Profit']/(p['Amount']*p['Price'])
        # Log('持仓成本:',p['Price'],'当前价格',ticker['Last'],'持仓数量',p['Amount'],'目前收益',p['Profit'],'目前收益率',yieldRate)
        global stopProfitRate

        # 止盈
        if yieldRate > stopProfitRate/1000 or (p['Amount']>50 and yieldRate >0):
            profit += p['Profit']
            
            # Log('止盈了','#ff0000@')
            if p.Type == PD_LONG:
                exchange.SetDirection('closebuy')
                exchange.Sell(ticker['Buy'], p['Amount'] - p['FrozenAmount'])

                buyUnit(ticker, positions, PositionChangeType.StopProfit)
            elif p.Type == PD_SHORT:
                exchange.SetDirection('closesell')
                exchange.Buy(ticker['Sell'], p['Amount'] - p['FrozenAmount'])
                sellUnit(ticker, positions, PositionChangeType.StopProfit)


        # 如果止损 4h内不做做单边补仓
        if yieldRate < -(stopLossRate/1000) or (yieldRate < 0 and p['Amount'] > 1):
            profit += p['Profit']
            
            if p.Type == PD_LONG:
                exchange.SetDirection('closebuy')
                exchange.Sell(ticker['Buy'], p['Amount'] - p['FrozenAmount'])
                buyUnit(ticker, positions, PositionChangeType.StopLoss)

                stopLossDict["long"] = ticker["Time"]
            elif p.Type == PD_SHORT:
                exchange.SetDirection('closesell')
                exchange.Buy(ticker['Sell'], p['Amount'] - p['FrozenAmount'])
                sellUnit(ticker, positions, PositionChangeType.StopLoss)
                stopLossDict["short"] = ticker["Time"]
  

lastTickerLast = 0
def tickerChange(ticker,positions):
    global lastTickerLast
    global isStopLossRest

    # 判断过激市场

    # last = ticker['Last']
    global stopLossDict
    if lastTickerLast != 0:
        # 价格差
        priceChange = (ticker['Last'] - lastTickerLast['Last'])
        # 时间差 /分钟
        timeGas = (ticker['Time'] - lastTickerLast['Time']) / (1000 * 60)
        # 每分钟变化率
        priceRateChange = (priceChange/lastTickerLast['Last']) / timeGas
        Log('价格变化:',priceChange, '相差时间:/s',timeGas, '相差率',priceRateChange,ticker['Time'], lastTickerLast['Time'])
        # Log('当前变动', priceChange*100,'%')

        # 跌的快，满足加仓条件 
        if priceRateChange < -0.002:
            # 开启止损休息 并改方向止损在4小时内 不加仓 
            if not(isStopLossRest and 'long' in stopLossDict.keys() and (ticker['Time'] - stopLossDict['long']) < 1000 * 60 * 60 * 4):
                buyUnit(ticker,positions,PositionChangeType.TirckerChange)

        if priceRateChange > 0.002:
            if not(isStopLossRest and 'short' in stopLossDict.keys() and (ticker['Time'] - stopLossDict['short']) < 1000 * 60 * 60 * 4):
                sellUnit(ticker,positions,PositionChangeType.TirckerChange)

    lastTickerLast = ticker


    
def onTick():
    ticker = exchange.GetTicker()
    positions = exchange.GetPosition()
   
    # 初始化仓位
    initPosition(ticker,positions)

    # 判断市场变化 逆向加仓
    tickerChange(ticker,positions)
        
    #查看仓位的收益
    disposePostion(ticker, positions)


#取消所有订单 && 平仓（TODO）
def cancelAllOrders():
    orders = exchange.GetOrders()
    for order in orders:
        exchange.CancelOrder(order["Id"])

def main():
    Log('开始执行')
    global lever
    global initAccount

    Log('杠杆倍数',lever)

    # 交易所配置
    exchange.SetContractType("swap")
    exchange.SetMarginLevel(lever)
    # 取消当前所有订单
    cancelAllOrders()
    # onTick()
    initAccount = exchange.GetAccount()

    while True:
        onTick()
        # 模拟时间
        r = 60 + random.randint(200,400)/1000
        # Log(r)
        Sleep(1000*r)



# 行情波动较大时，补仓

# 满足仓位盈利时 止盈 并开仓