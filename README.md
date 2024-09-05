# setAPI

## 部署

### 环境

> **python**：`3.9+`
>
> **库**：`flask`，`redis`，`requests`

### 安装

```shell
pip install -r flask redis requests
```

### 运行

```shell
python3.9 runSET.py
```

## 股票信息查询接口

> 查询股票名称，所属行业，查询分类等

**接口：**`/api/stockInfo`

**请求参数：**

| 参数名       | 参数值   | 备注           |
| ------------ | -------- | -------------- |
| code（可选） | 股票名称 | 示例：code=lee |

**返回值：**

> 前4个为通用参数，之后接口不再罗列

| 参数名    | 参数值        | 备注          |
| --------- | ------------- | ------------- |
| code      | 8200,8500     | api返回状态码 |
| symbol    | 股票名称      |               |
| timestamp | 时间戳        | 调用api的时间 |
| type      | 接口类型/描述 |               |

**DATA返回：**

| 参数名       | 返回值     | 备注 |
| ------------ | ---------- | ---- |
| asOfDate     | 查询时间   |      |
| industry     | 所属行业   |      |
| industryName | 行业全称   |      |
| market       | 所属市场   |      |
| otherIndices | \          |      |
| sector       | 子行业名称 |      |
| sectorName   | 子行业全称 |      |
| symbol       | 股票名称   |      |

`res示例`：

```json
请求路径：/api/stockInfo?code=lee

{
  "code": 8200,
  "data": {
    "asOfDate": "2023-11-24T00:00:00+07:00",
    "industry": "AGRO",
    "industryName": "Agro & Food Industry",
    "market": "SET",
    "otherIndices": [],
    "sector": "AGRI",
    "sectorName": "Agribusiness",
    "symbol": "lee"
  },
  "symbol": "lee",
  "timestamp": 1700813330.446977,
  "type": "单个股票信息查询"
}
```

## K线相关接口

> 查询k线相关信息，并根据更新频率存储redis

**接口：**`/api/history`

**请求参数：**

| 参数名 | 参数值   | 备注                                       |
| ------ | -------- | ------------------------------------------ |
| code   | 股票名称 | 示例：code=lee                             |
| period | 查询条件 | 1：盘中，1D：5Y日线，history：半年日线详情 |

**DATA返回（只说明个别特别值）：**

| 参数名        | 返回值             | 备注                           |
| ------------- | ------------------ | ------------------------------ |
| price         | 实际价格或者涨跌幅 | 盘中为实际价格，5Y日线为涨跌幅 |
| percentChange | 涨跌幅             | 查询半年日线详情有效           |

`res示例`：

```json

请求路径：/api/history?code=EE&period=1

{
  "code": 8200,
  "symbol": "EE",
  "timestamp": 1700813610.028448,
  "type": "K线盘中",
  "data": [
    {
      "close": null,
      "high": null,
      "low": null,
      "open": null,
      "percentChange": null,
      "price": 0.29,
      "time": 1700793900,
      "value": null,
      "volume": null
    },
    {
      "close": null,
      "high": null,
      "low": null,
      "open": null,
      "percentChange": null,
      "price": 0.29,
      "time": 1700793960,
      "value": null,
      "volume": null
    },
    {
      "close": null,
      "high": null,
      "low": null,
      "open": null,
      "percentChange": null,
      "price": 0.29,
      "time": 1700794020,
      "value": null,
      "volume": null
    }]
}
      
请求路径：/api/history?code=EE&period=1D
{
  "code": 8200,
  "symbol": "EE",
  "timestamp": 1700813691.357928,
  "type": "K线5Y",
  "data": [
    {
      "close": null,
      "high": null,
      "low": null,
      "open": null,
      "percentChange": null,
      "price": 0.0,
      "time": 1543165200,
      "value": null,
      "volume": null
    },
    {
      "close": null,
      "high": null,
      "low": null,
      "open": null,
      "percentChange": null,
      "price": 1.4925373134328477,
      "time": 1543251600,
      "value": null,
      "volume": null
    }]
}

请求路径：/api/history?code=EE&period=history
{
  "code": 8200,
  "symbol": "EE",
  "timestamp": 1700813741.196222,
  "type": "近6月详细历史数据"
  "data": [
    {
      "close": 0.29,
      "high": 0.3,
      "low": 0.29,
      "open": 0.3,
      "percentChange": -3.33,
      "price": null,
      "time": 1700672400,
      "value": 468260.17,
      "volume": 1571248.0
    },
    {
      "close": 0.3,
      "high": 0.3,
      "low": 0.29,
      "open": 0.3,
      "percentChange": 0.0,
      "price": null,
      "time": 1700586000,
      "value": 577545.79,
      "volume": 1937277.0
    },
    {
      "close": 0.3,
      "high": 0.3,
      "low": 0.28,
      "open": 0.3,
      "percentChange": 0.0,
      "price": null,
      "time": 1700499600,
      "value": 458893.55,
      "volume": 1575566.0
    }]
}
```

## 单个股票实时行情接口

> 单个股票实时价格查询，更全面

**接口：**`/api/price`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| code   | 股票名称 | 示例：code=lee |

**DATA返回（只说明个别特别值）：**

| 参数名 | 返回值 | 备注                      |
| ------ | ------ | ------------------------- |
| bids   | 买数据 | price：价格，volume：数量 |
| offers | 卖数据 | price：价格，volume：数量 |

`res返回示例`

```json
请求路径：/api/price?code=lee

{
  "code": 8200,
  "data": {
    "Amount": 64944.5,
    "bids": [
      {
        "price": "2.16",
        "volume": 9300.0
      }
    ],
    "buy1": null,
    "buyv1": null,
    "gain": -2.702703,
    "gainValue": -0.06,
    "high": 2.2,
    "low": 2.16,
    "name": "LEE FEED MILL PUBLIC COMPANY LIMITED",
    "nei": null,
    "neiv": null,
    "offers": [
      {
        "price": "2.22",
        "volume": 10000.0
      }
    ],
    "open": 2.2,
    "pb": 0.75,
    "pe": 29.5,
    "preClose": 2.22,
    "price": 2.16,
    "sell1": null,
    "sellv1": null,
    "symbol": "LEE",
    "volume": 30002.0,
    "wai": null,
    "waiv": null
  },
  "symbol": "lee",
  "timestamp": 1700813942.64299,
  "type": "实时股票查询"
}
```

## 所有股票信息查询

> 实时

**接口：**`/api/exchange`

**DATA返回（只说明个别特别值）：**

| 参数名 | 返回值 | 备注 |
| ------ | ------ | ---- |
| price  | 最新价 |      |

`res返回示例`

```json
请求路径：/api/exchange

{
  "code": 8200,
  "timestamp": 1700814095.08387,
  "type": "所有股票详情查询",
  "data": [
    {
      "gain": 3.448276,
      "gainValue": 0.01,
      "high": 0.3,
      "low": 0.29,
      "name": "ETERNAL ENERGY PUBLIC COMPANY LIMITED",
      "open": 0.3,
      "preClose": 0.29,
      "price": 0.3,
      "symbol": "EE",
      "volume": 351274.0
    },
    {
      "gain": -1.886792,
      "gainValue": -0.2,
      "high": 10.6,
      "low": 10.4,
      "name": "GFPT PUBLIC COMPANY LIMITED",
      "open": 10.5,
      "preClose": 10.6,
      "price": 10.4,
      "symbol": "GFPT",
      "volume": 224310.0
    },
    {
      "gain": -2.702703,
      "gainValue": -0.06,
      "high": 2.2,
      "low": 2.16,
      "name": "LEE FEED MILL PUBLIC COMPANY LIMITED",
      "open": 2.2,
      "preClose": 2.22,
      "price": 2.16,
      "symbol": "LEE",
      "volume": 30002.0
    }]
}
```

## 财报

### 股票公司最新财报

> 公司财报

**接口：**`/api/companyFinancial`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| code   | 股票名称 | 示例：code=lee |

### 股票财报

**接口：**`/api/financial`

**请求参数：**

| 参数名 | 参数值   | 备注                               |
| ------ | -------- | ---------------------------------- |
| type   | 财报类型 | 示例：now：当前财报，old：历史财报 |
| code   | 股票名称 | 示例：code=lee                     |

## 查询股票详细配置

> 公司名称，资产分配，上市时间，传真，邮件等等

**接口：**`/api/companyFinancial`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| code   | 股票名称 | 示例：code=lee |

## 股票持仓

> 查询普通持仓，NVDR持仓的前10名

**接口：**`/api/stockHolder`

**请求参数：**

| 参数名 | 参数值   | 备注                                  |
| ------ | -------- | ------------------------------------- |
| code   | 股票名称 | 示例：code=lee                        |
| type   | 持仓类型 | 示例：share：普通持仓，nvdr：NVDR持仓 |

## 股票所属公司最新动态

> 公告，通知等

**接口：**`/api/stockCompanyAction`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| code   | 股票名称 | 示例：code=lee |

## 市场告警

**接口：**`/api/marketAlert`

**请求参数：**

| 参数名 | 参数值 | 备注 |
| ------ | ------ | ---- |
| 无     |        |      |

## IPO相关

> 查询近期IPO的股票信息

**接口：**`/api/ipo`

**请求参数：**

| 参数名 | 参数值   | 备注                                                         |
| ------ | -------- | ------------------------------------------------------------ |
| type   | 查询类型 | 示例：upcoming：即将IPO，recently：近期已IPO，firstday：今天为IPO的第一天 |
| limit  | 查询条数 | 示例：5                                                      |

## 新闻

### 公共新闻

**接口：**`/api/publicNews`

**请求参数：**

| 参数名 | 参数值   | 备注                                                      |
| ------ | -------- | --------------------------------------------------------- |
| type   | 新闻类型 | 示例：company：公司，证券企业新闻，regulator：SET官方公告 |

### 股票新闻、资讯

**接口：**`/api/stocknews`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| limit  | 查询条数 | 示例：limit=5  |
| code   | 股票名称 | 示例：code=lee |

## 热门股票

**接口：**`/api/popular`

**请求参数：**

| 参数名       | 参数值         | 备注                                                         |
| ------------ | -------------- | ------------------------------------------------------------ |
| limit        | 查询条数       | 示例：limit=5                                                |
| market(可选) | 查询的市场类型 | 示例：<br />SET： set市场<br />mai： mai市场<br />默认为： SET |

## 股票交易排行

**接口：**`/api/topChart`

**请求参数：**

| 参数名 | 参数值   | 备注                                                         |
| ------ | -------- | ------------------------------------------------------------ |
| limit  | 查询条数 | 示例：limit=5                                                |
| type   | 查询类型 | 示例：<br />mostActiveVolume: 成交量排行      <br />mostActiveValue：成交额排行       <br />topLoser：跌幅排行                <br />topGainer：涨幅排行 |

## 大盘实时行情

**接口：**`/api/indexInfo`

**请求参数：**

| 参数名       | 参数值         | 备注                                                         |
| ------------ | -------------- | ------------------------------------------------------------ |
| type         | 查询的大盘类型 | 示例：INDEX: 市场大盘，industry：行业分类大盘                |
| market(可选) | 查询的市场类型 | 示例：<br />SET： set市场<br />mai： mai市场，注：**为mai时type类型只能为industry**<br />默认为： SET |

## 股票高亮数据

**接口：**`/api/highlight`

**请求参数：**

| 参数名 | 参数值   | 备注           |
| ------ | -------- | -------------- |
| code   | 股票名称 | 示例：code=lee |

## 股票分类列表

**接口：**`/api/stockindex`

**请求参数：**

| 参数名       | 参数值         | 备注                                                         |
| ------------ | -------------- | ------------------------------------------------------------ |
| level(可选)  | 列表级别       | 示例：<br />INDUSTRY：主行业分类<br />SECTOR：子行业分类<br />不传为所有分类，且为详细信息 |
| market(可选) | 查询的市场类型 | 示例：<br />SET： set市场<br />mai： mai市场，注：**为mai时level只能为INDUSTRY**<br />默认为： SET |