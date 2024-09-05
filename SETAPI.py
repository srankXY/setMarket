# -*- utf-8 -*-
#
import json
import requests
import redis
from SET.config import *


# SET API SDK形式
class SETAPI(object):
    """
    SET官方 api SDK形式，注：这样操作仅为方便改动，少调整代码
    """

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
                if i['symbol'] == symbol.upper():    # 统一大小写
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
    def redisOperator(method: str,  key: str, expire: int = 60, **kwargs):
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
        proxy = config.CONFIG.get('proxy')
    
        # 配置headers
        headers = {
            'Referer': 'https://www.set.or.th/',
            'X-Channel': 'WEB_SET',
            'X-Client-Uuid': 'db512e75-06b9-465f-a1a8-d68bda420458',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
    
        # 请求接口
        try:
            res = requests.get(url=base_url+path, headers=headers, proxies=proxy)
    
            return json.loads(res.content.decode('utf-8'))
    
        # 接口请求异常处理
        except Exception as e:
    
            print(path)
            return {
                "code": 8500,
                "msg": e
            }

if __name__ == '__main__':

    # AGRI - Agribusiness 分类下股票
    # url = 'https://www.set.or.th/api/set/index/agri/composition?lang=en&stock=LEE'
    # url = 'https://www.set.or.th/api/set/index/agri/composition?lang=en'

    last = SETAPI().getPopular(limit=5)
    # last = SETAPI.getPopular(limit=20)
    print(last)