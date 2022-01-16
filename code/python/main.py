# -*- coding: UTF-8 -*-

'''backtest
start: 2018-02-19 00:00:00
end: 2018-03-22 12:00:00
period: 15m
exchanges: [{"eid":"Bitfinex","currency":"BTC_USD","balance":10000,"stocks":3}]
'''

from fmz import *
import math
import talib

task = VCtx(__doc__)  # initialize backtest engine from __doc__


# ------------------------------ 策略部分开始 --------------------------


def adjustFloat(v):  # 策略中自定义的函数
    v = math.floor(v * 1000)
    return v / 1000


def onTick():
    Log("onTick")
    # 具体的策略代码


def main():
    account = exchange.GetAccount()
    ticker = exchange.GetTicker()
    print('account', account, 'ticker', ticker)
    Log('this is a little test')
    onTick()


# ------------------------------ 策略部分结束 --------------------------

# try:
#     # main()  # 回测结束时会 raise EOFError() 抛出异常，来停止回测的循环。所以要对这个异常处理，在检测到抛出的异常后调用 task.Join() 打印回测结果。
# except Exception as e:
#     print(e)
#     print(task.Join())

import requests
import urllib


def api_get(url, params: {} = None):
    """

    :param url:
    :param params:
    :return:
    """
    query_string = urllib.parse.urlencode(params) if params else ''
    print(query_string)
    return requests.get(url, params=params, proxies={'http': "socks5://127.0.0.1:9511",
                                                           'https': "socks5://127.0.0.1:9511"})

