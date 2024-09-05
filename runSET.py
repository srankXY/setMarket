# -*- utf-8 -*-
#

import json
import flask
import datetime
import requests
import redis
import functools
from ast import literal_eval
from SETAPI import *

# Flask API
api = flask.Flask(__name__)
api.json.ensure_ascii = False


# 通用异常处理，装饰器
def generalTryCatch(func):
    """
    通用异常装饰器
    :param func:    传入具体的函数名称以装饰该函数
    :return:
    """

    # 保留被装饰函数原始元数据
    @functools.wraps(func)
    # 装饰函数
    def wrapper(*args, **kwargs):

        # 异常捕获
        try:
            # 执行实际函数
            return func(*args, **kwargs)
        # 实际函数通用出错处理
        except Exception as e:
            # 调试打印
            print("函数%s, 出现异常： %s" % (func.__name__, e))
            # 异常返回
            return response(code=8500, result={
                'type': "错误",
                'data': "API调用失败，请联系管理员核实"
            })
    # 返回装饰函数
    return wrapper


# 返回框架
def response(code=8200, **kwargs):
    """
    :param code:    响应状态码
    :param kwargs:  返回的具体数据，示例：{'type': '盘中k线','symbol': 'LEE','data': result}，result为具体的k线数据
    :return:
    """

    data = {
        'code': code,
        'timestamp': datetime.datetime.now().timestamp()
    }

    # 根据传参重组返回数据
    for k, v in kwargs['result'].items():
        data[k] = v

    return data


# 股票信息查询接口
@api.route('/api/stockInfo', methods=['GET'])
def stockInfo():
    """
    :param: symbol可查询单个币种信息
    :return:
    """

    # 获取symbol参数
    symbol = flask.request.args.get('code')
    # 如果存在
    if symbol:

        return response(code=8200, result={
            'type': "单个股票信息查询",
            'symbol': symbol,
            'data': SETAPI().getStockInfo(symbol=symbol)
        })

    # 全部币种列表
    return response(code=8200, result={
        'type': "所有股票信息查询",
        'symbol': symbol,
        'data': SETAPI().getStockInfo()
    })


# k线和历史交易
@api.route('/api/history', methods=['GET'])
def kLine_History():
    """
    :param: symbol可查询币种的名称
    :return:
    """

    # 获取参数，code, period
    params = flask.request.args

    # 重组k线数据映射函数，适配盘中，5Y和history
    def klineMap(item):
        return {
            'time': int(datetime.datetime.strptime(item['datetime'] if 'datetime' in item else item['date'],
                                                   '%Y-%m-%dT%H:%M:%S%z').timestamp()),
            'close': item['close'] if 'close' in item else None,
            # 盘中price为实际价格，非盘中price为涨跌幅
            'price': item['price'] if 'price' in item else None,
            'percentChange': item['percentChange'] if 'percentChange' in item else None,
            'volume': item['volume'] if 'volume' in item else item['totalVolume'],
            'value': item['value'] if 'volume' in item else item['totalValue'],
            'high': item['high'] if 'high' in item else None,
            'low': item['low'] if 'low' in item else None,
            'open': item['open'] if 'open' in item else None
        }

    # redis 缓存函数
    def klineRedis(symbol: str, period: str):

        # 组装redis key
        KeyTime = datetime.datetime.now().strftime('%Y%m%d%H%M')
        redisKey = 'th_kline_data_' + KeyTime + '_' + period + '_' + symbol

        # redis 取值
        redisKlineValue = SETAPI().redisOperator(method='GET', key=redisKey)

        # 如果存在则直接返回
        if redisKlineValue:
            return response(code=8200, result={
                'type': redisKey,
                'symbol': symbol,
                'data': literal_eval(redisKlineValue.decode('utf-8'))
            })

        # 无缓存情况的处理
        result = "API调用失败，请联系管理员核实"
        try:
            # 判断period
            if period == '1D':

                # 定义接口描述
                type = 'K线5Y'
                # 查询5Y
                result = SETAPI().getKline(symbol=params.get('code'), period='5Y')
                # 重组数据
                kline_data = list(map(klineMap, result['quotations']))

            else:

                # 定义接口描述
                type = '近6月详细历史数据'
                # 查询近6月历史交易详情
                result = SETAPI().getKlineHistory(symbol=params.get('code'))
                # 重组数据
                kline_data = list(map(klineMap, result))

        # set api返回数据异常处理
        except Exception as e:
            print(e)
            return response(code=8500, result={
                'type': "错误",
                'data': result
            })

        # 缓存进redis
        SETAPI().redisOperator(method='SET', key=redisKey, value=str(kline_data))

        # 返回
        return response(code=8200, result={
            'type': type,
            'symbol': symbol,
            'data': kline_data
        })

    # kline函数核心逻辑
    # 当日盘中数据
    if params.get('period') == '1':

        result = SETAPI().getKline(symbol=params.get('code'), period='1D')

        # 重组数据并返回
        try:
            kline_data = list(map(klineMap, result['quotations']))
            return response(code=8200, result={
                'type': "K线盘中",
                'symbol': params.get('code'),
                'data': kline_data
            })
        # 异常处理
        except:
            return response(code=8500, result={
                'type': "错误",
                'data': result
            })

    # 获取5Y数据、历史交易
    else:
        # 返回
        return klineRedis(symbol=params.get('code'), period=params.get('period'))


# 股票实时行情接口
@api.route('/api/price', methods=['GET'])
def price():
    """
    :param: symbol可查询单个币种信息
    :return:
    """

    # 获取symbol参数
    symbol = flask.request.args.get('code')

    # 获取币种详情
    stockDetails = SETAPI().getStockInfo(symbol=symbol)

    # 获取对应币种的sector
    sector = stockDetails['sector']
    # 处理个别股票不存在sector，并且market为mai的情况
    if stockDetails['market'] == 'mai':
        # 重组mai市场行业列表名称
        sector = SETAPI().getStockInfo(symbol=symbol)['industry'].lower() + '-m'

    # 获取set api原始数据
    # conposition 数据
    compositionResult = SETAPI().getStockTrade(sector=sector, symbol=symbol)
    # highlight 数据
    highlightResult = SETAPI().getHighLight(symbol=symbol)

    # 重组股票数据
    newStockInfo = {
        'name': compositionResult['nameEN'],
        'symbol': compositionResult['symbol'],
        'price': compositionResult['last'],
        'open': compositionResult['open'],
        'preClose': compositionResult['prior'],
        'volume': compositionResult['totalVolume'],
        'gain': compositionResult['percentChange'],
        'gainValue': compositionResult['change'],
        'high': compositionResult['high'],
        'low': compositionResult['low'],
        'Amount': compositionResult['totalValue'],
        'pe': highlightResult['peRatio'],
        'pb': compositionResult['pbRatio'],
        'bids': compositionResult['bids'],
        'offers': compositionResult['offers'],
        'buy1': None,
        'buyv1': None,
        'sell1': None,
        'sellv1': None,
        'nei': None,
        'wai': None,
        'neiv': None,
        'waiv': None,
    }

    # 返回
    return response(code=8200, result={
        'type': "实时股票查询",
        'symbol': symbol,
        'data': newStockInfo
    })


# 所有股票信息返回
@api.route('/api/exchange', methods=['GET'])
def exchange():
    """
    :return:    返回所有股票详细信息
    """

    # 所有股票列表
    allStocks = []

    # 获取SET市场分类列表
    setIndustryList = SETAPI().getStockIndex(level='INDUSTRY')
    # 获取mai市场分类列表
    maiIndustryList = SETAPI().getStockIndex(level='INDUSTRY', market='mai')

    # 数据整理
    def stockMap(item):
        return {
            'name': item['nameEN'],
            'symbol': item['symbol'],
            'price': item['last'],
            'open': item['open'],
            'preClose': item['prior'],
            'gain': item['percentChange'],
            'gainValue': item['change'],
            'high': item['high'],
            'low': item['low'],
            'volume': item['totalVolume'],
        }

    try:
        # 遍历循环SET, mai分类获取所有股票
        for industry in setIndustryList + maiIndustryList:
            indexStock = SETAPI().getStockTrade(sector=industry, symbol='all')

            # 判断行业下没有股票的情况
            if indexStock is None:
                continue

            # 重组数据
            mapStocks = list(map(stockMap, indexStock))
            allStocks += mapStocks

    except Exception as e:
        print(e)
        return response(code=8500, result={
            'type': "错误",
            'data': "获取所有股票信息失败，请联系管理官"
        })

    # 返回
    return response(code=8200, result={
        'type': "所有股票详情查询",
        'data': allStocks
    })


# 获取股票分类列表
@api.route('/api/stockindex', methods=['GET'])
@generalTryCatch
def stockindex():
    """
    :param: market（可选） 查询的市场类型，可为：SET，mai，默认为SET
    :param: level（可选）,查询的类型，可为：INDUSTRY, SECTOR
    :return:
    """

    # 获取参数
    params = flask.request.args
    level = params.get('level')

    market = 'SET'
    if 'market' in params:
        market = params.get('market')

    # 返回
    return response(code=8200, result={
        'type': "股票行业信息查询",
        'level': level,
        'market': market,
        'data': SETAPI().getStockIndex(level=level, market=market)
    })


# 获取高亮数据
@api.route('/api/highlight', methods=['GET'])
@generalTryCatch
def highlight():
    """
    :parame: code  查询的股票名称
    :return:
    """

    # 获取参数
    symbol = flask.request.args.get('code')

    # 返回
    return response(code=8200, result={
        'type': "股票高亮数据返回",
        'symbol': symbol,
        'data': SETAPI().getHighLight(symbol=symbol)
    })


# 获取股票资讯信息
@api.route('/api/stocknews', methods=['GET'])
@generalTryCatch
def stockNews():
    """
    :param: code 查询的股票名称
    :param: limit 查询的新闻条数
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 返回
    return response(code=8200, result={
        'type': "新闻、资讯查询",
        'symbol': params.get('code'),
        'data': SETAPI().getStockNews(symbol=params.get('code'), limit=params.get('limit'))
    })


# 获取财报信息
@api.route('/api/financial', methods=['GET'])
@generalTryCatch
def financial():
    """
    :param: code 查询的股票名称
    :param: type 查询类型，now：当前财报，old：历史财报
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 参数判断
    if params.get('type') == 'now':
        # 本年财报
        result = SETAPI().getCurrentFinancial(symbol=params.get('code'))
    # 往年财报
    else:
        result = SETAPI().getOldFinancial(symbol=params.get('code'))

    # 返回
    return response(code=8200, result={
        'type': "股票财报查询",
        'symbol': params.get('code'),
        'financialType': params.get('type'),
        'data': result
    })


# 获取市场，分类大盘实时数据
@api.route('/api/indexInfo', methods=['GET'])
@generalTryCatch
def indexInfo():
    """
    :param: type 查询类型，INDEX: 市场大盘，industry：行业分类大盘
    :param: market(可选) 查询市场，SET，mai
    :return:
    """

    # 获取参数
    params = flask.request.args
    type = params.get('type')
    market = 'SET'          # 默认 SET 市场

    # mai 市场
    if 'market' in params:
        market = params.get('market')

    # 返回
    return response(code=8200, result={
        'type': "大盘行情查询",
        'indexInfoType': type,
        'market': market,
        'data': SETAPI().getIndexTrade(type=type, market=market)
    })


# 获取当前市场交易数据排行榜
@api.route('/api/topChart', methods=['GET'])
@generalTryCatch
def topChart():
    """
    :param type: 指定查询类型，mostActiveVolume: 成交量排行，mostActiveValue：成交额排行
                                topLoser：跌幅排行，topGainer：涨幅排行
    :param limit: 返回条数
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 返回
    return response(code=8200, result={
        'type': "交易数据排行榜查询",
        'topListType': params.get('type'),
        'data': SETAPI().getTopList(type=params.get('type'), limit=int(params.get('limit')))
    })


# 获取热门股票
@api.route('/api/popular', methods=['GET'])
@generalTryCatch
def popular():
    """
    :param market: (可选),查询的市场类型，可为：SET，mai
    :param limit: 查询条数
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 返回
    return response(code=8200, result={
        'type': "热门股票查询",
        'market': params.get('market'),
        'data': SETAPI().getPopular(limit=int(params.get('limit')), market=params.get('market'))
    })


# 获取公共新闻
@api.route('/api/publicNews', methods=['GET'])
@generalTryCatch
def publicNews():
    """
    :param type: 公共新闻查询类型，company：公司，证券企业新闻，regulator：SET官方公告
    :return:
    """

    # 获取参数
    type = flask.request.args.get('type')

    # 返回
    return response(code=8200, result={
        'type': "公共新闻查询",
        'publicNewsType': type,
        'data': SETAPI().getPublicNews(type=type)
    })


# 查询IPO信息
@api.route('/api/ipo', methods=['GET'])
@generalTryCatch
def ipo():
    """
    :param type: 查询的IPO信息类型，upcoming：即将IPO，recently：最近IPO，firstday：今天为IPO的第一天
    :param limit: 查询条数
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 返回
    return response(code=8200, result={
        'type': "IPO数据查询",
        'IPOType': params.get('type'),
        'data': SETAPI().getIPOInfo(type=params.get('type'), limit=int(params.get('limit')))
    })


# 市场警告信息查询
@api.route('/api/marketAlert', methods=['GET'])
@generalTryCatch
def marketAlert():
    """
    :return:
    """

    # 返回
    return response(code=8200, result={
        'type': "SET市场警告信息",
        'data': SETAPI().getMarketAlert()
    })


# 封装api查询股票所属公司最新动态
@api.route('/api/stockCompanyAction', methods=['GET'])
@generalTryCatch
def stockCompanyAction():
    """
    :param code:  查询的股票名称
    :return:
    """

    # 获取参数
    symbol = flask.request.args.get('code')

    # 返回
    return response(code=8200, result={
        'type': "公司动态查询",
        'symbol': symbol,
        'data': SETAPI().getStockCompanyAction(symbol=symbol)
    })


# 查询股票持仓情况
@api.route('/api/stockHolder', methods=['GET'])
@generalTryCatch
def stockHolder():
    """
    :param code:  查询的股票名称
    :param type:  查询的持仓类型，share：普通持仓，nvdr：nvdr持仓
    :return:
    """

    # 获取参数
    params = flask.request.args

    # 判断type为NVDR的情况
    if params.get('type') == 'nvdr':
        params['type'] = 'nvdr-'

    # 返回
    return response(code=8200, result={
        'type': "股票持仓信息查询(前10)",
        'symbol': params.get('symbol'),
        'data': SETAPI().getStockHolder(symbol=params.get('symbol'), type=params.get('type'))
    })


# 查询股票详细信息，所属公司等
@api.route('/api/stockProfile', methods=['GET'])
@generalTryCatch
def stockProfile():
    """
    :param code:  查询的股票名称
    :return:
    """

    # 获取参数
    symbol = flask.request.args.get('code')

    # 返回
    return response(code=8200, result={
        'type': "股票详细信息查询(所属公司等)",
        'symbol': symbol,
        'data': SETAPI().getStockProfile(symbol=symbol)
    })


# 查询股票所属公司最新财报
@api.route('/api/companyFinancial', methods=['GET'])
@generalTryCatch
def companyFinancial():
    """
    :param code:  查询的股票名称
    :return:
    """

    # 获取参数
    symbol = flask.request.args.get('code')

    # 返回
    return response(code=8200, result={
        'type': "股票所属企业最新财报查询",
        'symbol': symbol,
        'data': SETAPI().getCompanyFinancial(symbol=symbol)
    })

if __name__ == '__main__':
    api.run(port=8888, debug=True, host='0.0.0.0')