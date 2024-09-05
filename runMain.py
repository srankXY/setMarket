# -*- utf-8 -*-
#

import json
import flask
import datetime
import requests
import redis
import functools
from ast import literal_eval


# config 类
class config(object):
    """
    外部配置，注：这样操作仅为方便改动，少调整代码
    """
    CONFIG = {
        # 代理
        'proxy': {
            'https': 'http://127.0.0.1:7890'
        },

        # 网络请求重试
        'retry': 3,

        # redis
        'redisHost': '172.31.1.1',
        'redisPort': 6379,
        'redisDB': 0,
        'redisPassword': 'foobared',
    }


# SET API SDK形式
class SETAPI(object):
    """
    SET官方 api SDK形式，注：这样操作仅为方便改动，少调整代码
    """

    def __init__(self):
        self.proxy = config.CONFIG.get('proxy')
        # 配置headers
        self.headers = {
            'authority': 'www.set.or.th',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.set.or.th/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'X-Channel': 'WEB_SET',
            'X-Client-Uuid': 'db512e75-06b9-465f-a1a8-d68bda420458',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36'
        }

    # 股票所属公司的最新财报
    def getCompanyFinancial(self, symbol: str):
        """
        :param symbol:  查询的股票名称
        :return:
        """

        # 定义路径
        path = '/set/stock/%s/financialstatement/latest-full-financialstatement?lang=en' % symbol

        # 返回数据
        return self.doGET(path)

    # 股票持仓查询
    def getStockProfile(self, symbol: str):
        """
        :param symbol:  查询的股票名称
        :return:
        """

        # 定义路径
        path = '/set/company/%s/profile?lang=en' % symbol

        # 返回数据
        return self.doGET(path)

    # 股票持仓查询
    def getStockHolder(self, symbol: str, type: str):
        """
        :param symbol:  查询的股票名称
        :param type:  查询的持仓类型，share：普通持仓，nvdr：nvdr持仓
        :return:
        """

        # 定义路径
        path = '/set/stock/%s/%sholder?lang=en' % (symbol, type)

        # 返回数据
        return self.doGET(path)

    # 获取股票所属公司最新动态
    def getStockCompanyAction(self, symbol: str):
        """
        :param symbol:  查询的股票名称
        :return:
        """

        # 定义路径
        path = '/set/stock/%s/corporate-action?lang=en' % symbol

        # 返回数据
        return self.doGET(path)

    # 获取市场警告信息
    def getMarketAlert(self):
        """
        :return:
        """

        # 定义路径
        path = '/set/news/market-alert?lang=en'

        # 返回数据
        return self.doGET(path)

    # IPO接口
    def getIPOInfo(self, type: str, limit: int):
        """
        :param type: 查询的IPO信息类型，upcoming：即将IPO，recently：最近IPO，firstday：今天为IPO的第一天
        :param limit: 查询条数
        :return:
        """

        # 定义路径
        path = '/set/ipo/%s?limit=%d&lang=en' % (type, limit)

        # 返回数据
        return self.doGET(path)

    # 获取公共新闻
    def getPublicNews(self, type: str):
        """
        :param type: 公共新闻查询类型，company：公司，证券企业新闻，regulator：SET官方公告
        :return:
        """

        # 定义路径
        path = '/set/news/search?sourceId=%s&lang=en' % type

        # 返回数据
        return self.doGET(path)

    # 获取股票热门搜索列表
    def getPopular(self, limit: int, market: str = None):
        """
        :param market: （可选），查询的市场类型，可为：SET，mai
        :param limit: 查询条数
        :return:
        """

        # 设置默认 market
        if market is None:
            market = 'SET'

        # 定义路径
        path = '/cms/v1/popularquote/getpopular?market=%s&securityType=S&limit=%d' % (market, limit)

        # 返回数据
        return self.doGET(path)

    # 获取当前行情排行榜
    def getTopList(self, type: str, limit: int):
        """
        :param type: 指定查询类型，mostActiveVolume: 成交量排行，mostActiveValue：成交额排行
                                topLoser：跌幅排行，topGainer：涨幅排行
        :param limit: 返回条数，必须为int类型
        :return:
        """

        # 定义路径
        path = '/set/ranking/%s/SET/S?count=%d' % (type, limit)

        # 返回数据
        return self.doGET(path)

    # 获取市场、行业分类大盘实时行情
    def getIndexTrade(self, type: str, market: str = 'SET'):
        """
        :param market: 市场类型，SET，mai
        :param type: 指定查询类型，INDEX: 市场大盘，industry：行业分类大盘
        :return:
        """

        # 定义路径
        path = '/set/index/info/list?type=%s&market=%s&lang=en' % (type, market)

        # 返回数据
        return self.doGET(path)

    # 获取股票对应的资讯信息
    def getStockNews(self, symbol: str, limit):
        """
        :param limit:  查询的条数
        :param symbol: 股票名称
        :return:
        """

        # 定义路径
        path = '/set/news/%s/list?lang=en&limit=%s' % (symbol, limit)

        # 返回数据
        return self.doGET(path)

    # 获取本年财报
    def getCurrentFinancial(self, symbol: str):
        """
        :param symbol: 查询的股票名称
        :return:
        """

        # 定义路径
        path = '/set/stock/%s/key-financial-data?lang=en' % symbol

        # 返回数据
        return self.doGET(path)

    # 获取往年财报历史
    def getOldFinancial(self, symbol: str):
        """
        :param symbol: 查询的股票名称
        :return:
        """

        # 定义路径
        path = '/set/stock/%s/company-highlight/financial-data?lang=en' % symbol

        # 返回数据
        return self.doGET(path)

    # 获取股票分类列表
    def getStockIndex(self, level: str = None, market: str = 'SET'):
        """
        :param market: 查询的市场类型，可为：SET，mai，默认为SET
        :param level:  查询的类型，可为：INDUSTRY, SECTOR, 默认为None
        :return:
        """

        # 路径
        path = '/set/index/list?type=industry&market=%s&lang=en' % market

        # 执行请求
        result = self.doGET(path)

        # 返回完整原始数据
        if level is None:
            return result

        # 返回简洁列表
        # 数据映射函数
        def stockIndexMap(item):
            if item['level'] == level.upper():
                return item['symbol'] if market != 'mai' else item['symbol'] + '-M'

        # 重组数据
        stockIndex = list(filter(None, map(stockIndexMap, result)))

        # 返回
        return stockIndex

    # 获取所有股票信息
    def getStockInfo(self, **kwargs):
        """
        :param kwargs: 传入股票名称进行单个股票信息查询，如：{'symbol': 'LEE'}
        :return:
        """

        # 判断是否传入参数
        if 'symbol' in kwargs:
            path = "/set/stock/%s/index-list?lang=en" % kwargs['symbol']
            return self.doGET(path)

        # 处理通用情况
        # 接口请求
        path = "/set/stock/list"
        return self.doGET(path)

    # 股票实时数据
    def getStockTrade(self, sector: str, symbol: str):
        """
        :param sector: 行业查询名称(股票所属行业)，主要为加快查询速度
        :param symbol: 股票名称，all表示所有
        :return:
        """

        # 路径
        path = "/set/index/%s/composition?lang=en" % sector

        # 执行请求
        result = self.doGET(path)

        # 获取股票列表异常捕获
        try:
            # 获取对应分类下的股票列表
            stockInfos = result['composition']['stockInfos']

            # 判断为industry的情况
            if stockInfos is None:

                stockInfos = []
                # 循环 industry 分类下的所有子行业
                for item in result['composition']['subIndices']:
                    stockInfos += item['stockInfos']

        # 处理行业股票列表为空的情
        except Exception as e:
            pass

        # 直接返回分类下所有股票
        if symbol == 'all':
            return stockInfos

        try:
            # 遍历取对应的股票信息， 单个股票查询
            for i in stockInfos:
                if i['symbol'] == symbol.upper():  # 统一大小写
                    # 返回对应股票数据
                    return i

        except:
            # 处理数据未查找到的情况
            return {
                'code': 8404,
                'msg': '股票交易未找到，请核实股票名称，或者该股票只存在于列表中没有实际的数据'
            }

    # k 线历史交易
    def getKlineHistory(self, symbol: str):
        """
        :param symbol: 查询条件，股票名称
        :return:
        """

        # 路径
        path = "/set/stock/%s/historical-trading?lang=en" % symbol

        # 请求
        return self.doGET(path)

    # 其他k线（盘中，1月，1年等）
    def getKline(self, symbol: str, period: str):
        """
        :param symbol:  查询股票名称
        :param period:  查询周期（1D：盘中，1/3/6M：1/3/6月，1/3/5Y：1/3/5年）
        :return:
        """

        # 默认path为ID条件查询
        path = "/set/stock/%s/chart-quotation?period=1D&accumulated=false" % symbol

        # 处理path，accumulated意为积累，在k线中为一段时间
        if period != '1D':
            path = "/set/stock/%s/chart-performance?period=%s&accumulated=true" % (symbol, period)

        # 执行请求
        return self.doGET(path)

    # 获取高亮数据（市盈率，市值等）
    def getHighLight(self, symbol: str):
        """
        :param symbol:  查询的股票名称
        :return:
        """

        # 路径
        path = "/set/stock/%s/highlight-data?lang=en" % symbol

        # 请求
        return self.doGET(path)

    # redis 操作
    @staticmethod
    def redisOperator(method: str, key: str, expire: int = 60, **kwargs):
        """
        :param method:  操作方法
        :param expire:  key过期时间，默认60s
        :param key:     redis key名称
        :param kwargs:  可选参数，用于传value，示例：kwargs['value']
        :return:
        """

        # 连接redis
        r = redis.Redis(
            host=config.CONFIG.get('redisHost'),
            port=config.CONFIG.get('redisPort'),
            db=config.CONFIG.get('redisDB'),
            password=config.CONFIG.get('redisPassword')
        )

        # redis 全局异常捕获
        try:

            # 取key逻辑
            if method == 'GET':

                # 判断key是否存在
                if r.exists(key):
                    # 返回数据并关闭连接
                    result = r.get(key)
                    r.close()
                    return result

                # 不存在返回false
                r.close()
                return False

            # 设置key
            elif method == 'SET':

                # 设置key，并返回状态
                result = r.setex(key, expire, kwargs['value'])
                r.close()
                return result

        # 处理redis异常
        except Exception as e:
            print(e)
            return False

    # 执行网络请求func
    def doGET(self, path: str):
        """
        :param path:    请求路径
        :return:
        """

        # 基本参数配置
        base_url = "https://www.set.or.th/api"
        global Cookies
        # 创建session
        session = requests.Session()
        session.cookies.update(Cookies)
        # 请求重试
        res = None
        for i in range(config.CONFIG.get('retry')):
            # 请求接口
            try:
                res = session.get(url=base_url + path, headers=self.headers, proxies=self.proxy)
                # 数据正确则退出，不正确则刷新session
                if res is not None and res.status_code == 200:
                    break
                else:
                    session.get(url='https://www.set.or.th/', headers=self.headers,
                                proxies=self.proxy)
                    Cookies = session.cookies.get_dict()

            # 接口请求异常处理
            except Exception as e:
                print("接口 %s 第 %d 次请求失败，具体错误: %s" % (path, i + 1, str(e)))

        # 返回
        if res is None or res.status_code != 200:
            return {
                "code": 8500,
                "msg": "接口 %s 请求失败" % path
            }
        else:
            return json.loads(res.content.decode('utf-8'))


Cookies = {}

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
@generalTryCatch
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
@generalTryCatch
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
@generalTryCatch
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
@generalTryCatch
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
    market = 'SET'  # 默认 SET 市场

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
