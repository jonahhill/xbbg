# xbbg

|                |                                                                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Latest Release | [![PyPI version](https://img.shields.io/pypi/v/xbbg.svg)](https://badge.fury.io/py/xbbg)                                                             |
|                | [![PyPI version](https://img.shields.io/pypi/pyversions/xbbg.svg)](https://badge.fury.io/py/xbbg)                                                    |
| Docs           | [![Documentation Status](https://readthedocs.org/projects/xbbg/badge/?version=latest)](https://xbbg.readthedocs.io/en/latest)                        |
| Build          | [![Travis CI](https://img.shields.io/travis/alpha-xone/xbbg/master.svg?logo=travis&label=Travis%20CI)](https://travis-ci.com/alpha-xone/xbbg)        |
|                | [![Azure](https://dev.azure.com/alpha-xone/xbbg/_apis/build/status/alpha-xone.xbbg)](https://dev.azure.com/alpha-xone/xbbg/_build)                   |
| Coverage       | [![codecov](https://codecov.io/gh/alpha-xone/xbbg/branch/master/graph/badge.svg)](https://codecov.io/gh/alpha-xone/xbbg)                             |
| Quality        | [![Codacy Badge](https://api.codacy.com/project/badge/Grade/2ec89be198cf4689a6a6c6407b0bc965)](https://www.codacy.com/app/alpha-xone/xbbg)           |
|                | [![CodeFactor](https://www.codefactor.io/repository/github/alpha-xone/xbbg/badge)](https://www.codefactor.io/repository/github/alpha-xone/xbbg)      |
|                | [![codebeat badge](https://codebeat.co/badges/eef1f14d-72eb-445a-af53-12d3565385ec)](https://codebeat.co/projects/github-com-alpha-xone-xbbg-master) |
| License        | [![GitHub license](https://img.shields.io/github/license/alpha-xone/xbbg.svg)](https://github.com/alpha-xone/xbbg/blob/master/LICENSE)               |

Bloomberg data toolkit for humans

## Requirements

- Bloomberg C++ SDK version 3.12.1 or higher:

    - [Bloomberg API Library](https://www.bloomberg.com/professional/support/api-library/)

    - Downlaod C++ Experimental Release

    - Copy `blpapi3_32.dll` and `blpapi3_64.dll` under `bin` 
      folder to Bloomberg `BLPAPI_ROOT` folder, normally `blp/DAPI`

- Bloomberg Open API (need to install manually as shown below)

- [pdblp](https://github.com/matthewgilbert/pdblp) - pandas wrapper for Bloomberg Open API

- numpy, pandas, ruamel.yaml and pyarrow

## Installation

```cmd
pip install blpapi --index-url=https://bloomberg.bintray.com/pip/simple
pip install xbbg
```

## What's New

_0.1.22_ - Remove PyYAML dependency due to security vulnerability

_0.1.17_ - Add `adjust` argument in `bdh` for easier dividend / split adjustments

## Tutorial

```python
In[1]: from xbbg import blp
```

### Basics

- ``BDP`` example:

```python
In[2]: blp.bdp(tickers='NVDA US Equity', flds=['Security_Name', 'GICS_Sector_Name'])
```

```pydocstring
Out[2]:
               security_name        gics_sector_name
ticker
NVDA US Equity   NVIDIA Corp  Information Technology
```

- ``BDP`` with overrides:

```python
In[3]: blp.bdp('AAPL US Equity', 'Eqy_Weighted_Avg_Px', VWAP_Dt='20181224')
```

```pydocstring
Out[3]: 
                eqy_weighted_avg_px
ticker
AAPL US Equity               148.75
```

- ``BDH`` example:

```python
In[4]: blp.bdh(
  ...:     tickers='SPX Index', flds=['high', 'low', 'last_price'],
  ...:     start_date='2018-10-10', end_date='2018-10-20',
  ...: )
```

```pydocstring
Out[4]:
ticker     SPX Index
field           high      low last_price
2018-10-10  2,874.02 2,784.86   2,785.68
2018-10-11  2,795.14 2,710.51   2,728.37
2018-10-12  2,775.77 2,729.44   2,767.13
2018-10-15  2,775.99 2,749.03   2,750.79
2018-10-16  2,813.46 2,766.91   2,809.92
2018-10-17  2,816.94 2,781.81   2,809.21
2018-10-18  2,806.04 2,755.18   2,768.78
2018-10-19  2,797.77 2,760.27   2,767.78
```

- ``BDH`` example with Excel compatible inputs:

```python
In[4]: blp.bdh(
  ...:     tickers='SHCOMP Index', flds=['high', 'low', 'last_price'],
  ...:     start_date='2018-09-26', end_date='2018-10-20',
  ...:     Per='W', Fill='P', Days='A',
  ...: )
```

```pydocstring
Out[4]:
ticker     SHCOMP Index
field              high      low last_price
2018-09-28     2,827.34 2,771.16   2,821.35
2018-10-05     2,827.34 2,771.16   2,821.35
2018-10-12     2,771.94 2,536.66   2,606.91
2018-10-19     2,611.97 2,449.20   2,550.47
```

- ``BDH`` without adjustment for dividends and splits:

```python
In[5]: blp.bdh(
  ...:     'AAPL US Equity', 'px_last', '20140605', '20140610',
  ...:     CshAdjNormal=False, CshAdjAbnormal=False, CapChg=False
  ...: )
```

```pydocstring
Out[5]: 
ticker     AAPL US Equity
field             px_last
2014-06-05         647.35
2014-06-06         645.57
2014-06-09          93.70
2014-06-10          94.25
```

- ``BDH`` adjusted for dividends and splits:

```python
In[6]: blp.bdh(
  ...:     'AAPL US Equity', 'px_last', '20140605', '20140610',
  ...:     CshAdjNormal=True, CshAdjAbnormal=True, CapChg=True
  ...: )
```

```pydocstring
Out[6]:
ticker     AAPL US Equity
field             px_last
2014-06-05          85.45
2014-06-06          85.22
2014-06-09          86.58
2014-06-10          87.09
```

- ``BDS`` example:

```python
In[7]: blp.bds('AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20180101', DVD_End_Dt='20180531')
```

```pydocstring
Out[7]:
               declared_date     ex_date record_date payable_date  dividend_amount dividend_frequency dividend_type
ticker
AAPL US Equity    2018-05-01  2018-05-11  2018-05-14   2018-05-17             0.73            Quarter  Regular Cash
AAPL US Equity    2018-02-01  2018-02-09  2018-02-12   2018-02-15             0.63            Quarter  Regular Cash
```

- Intraday bars ``BDIB`` example:

```python
In[8]: blp.bdib(ticker='BHP AU Equity', dt='2018-10-17').tail()
```

```pydocstring
Out[8]:
ticker                    BHP AU Equity
field                              open  high   low close   volume num_trds
2018-10-17 15:56:00+11:00         33.62 33.65 33.62 33.64    16660      126
2018-10-17 15:57:00+11:00         33.65 33.65 33.63 33.64    13875      156
2018-10-17 15:58:00+11:00         33.64 33.65 33.62 33.63    16244      159
2018-10-17 15:59:00+11:00         33.63 33.63 33.61 33.62    16507      167
2018-10-17 16:10:00+11:00         33.66 33.66 33.66 33.66  1115523      216
```

Above example works because 1) `AU` in equity ticker is mapped to `EquityAustralia` in
`markets/assets.yml`, and 2) `EquityAustralia` is defined in `markets/exch.yml`.
To add new mappings, define `BBG_ROOT` in sys path and add `assets.yml` and 
`exch.yml` under `BBG_ROOT/markets`.

- Intraday bars within market session:

```python
In[9]: blp.intraday(ticker='7974 JT Equity', dt='2018-10-17', session='am_open_30').tail()
```

```pydocstring
Out[9]:
ticker                    7974 JT Equity
field                               open      high       low     close volume num_trds
2018-10-17 09:27:00+09:00      39,970.00 40,020.00 39,970.00 39,990.00  10800       44
2018-10-17 09:28:00+09:00      39,990.00 40,020.00 39,980.00 39,980.00   6300       33
2018-10-17 09:29:00+09:00      39,970.00 40,000.00 39,960.00 39,970.00   3300       21
2018-10-17 09:30:00+09:00      39,960.00 40,010.00 39,950.00 40,000.00   3100       19
2018-10-17 09:31:00+09:00      39,990.00 40,000.00 39,980.00 39,990.00   2000       15
```

- Corporate earnings:

```python
In[10]: blp.earning('AMD US Equity', by='Geo', Eqy_Fund_Year=2017, Number_Of_Periods=1)
```

```pydocstring
Out[10]:
                 level    fy2017  fy2017_pct
Asia-Pacific      1.00  3,540.00       66.43
    China         2.00  1,747.00       49.35
    Japan         2.00  1,242.00       35.08
    Singapore     2.00    551.00       15.56
United States     1.00  1,364.00       25.60
Europe            1.00    263.00        4.94
Other Countries   1.00    162.00        3.04
```

- Dividends:

```python
In[11]: blp.dividend(['C US Equity', 'MS US Equity'], start_date='2018-01-01', end_date='2018-05-01')
```

```pydocstring
Out[11]:
                dec_date     ex_date    rec_date    pay_date  dvd_amt dvd_freq      dvd_type
ticker
C US Equity   2018-01-18  2018-02-02  2018-02-05  2018-02-23     0.32  Quarter  Regular Cash
MS US Equity  2018-04-18  2018-04-27  2018-04-30  2018-05-15     0.25  Quarter  Regular Cash
MS US Equity  2018-01-18  2018-01-30  2018-01-31  2018-02-15     0.25  Quarter  Regular Cash
```

-----

*New in 0.1.17* - Dividend adjustment can be simplified to one parameter `adjust`:

- ``BDH`` without adjustment for dividends and splits:

```python
In[12]: blp.bdh('AAPL US Equity', 'px_last', '20140606', '20140609', adjust='-')
```

```pydocstring
Out[12]:
ticker     AAPL US Equity
field             px_last
2014-06-06         645.57
2014-06-09          93.70
```

- ``BDH`` adjusted for dividends and splits:

```python
In[13]: blp.bdh('AAPL US Equity', 'px_last', '20140606', '20140609', adjust='all')
```

```pydocstring
Out[13]:
ticker     AAPL US Equity
field             px_last
2014-06-06          85.22
2014-06-09          86.58
```

### Optimizations

This library uses a global Bloomberg connection on the backend - 
more specically, `_xcon_` in `globals()` variable.
Since initiation of connections takes time, if multiple queries are expected,
manual creation of a new connection (which will be shared by all following queries)
is helpful before calling any queries.

- In command line, below command is helpful:

```python
from xbbg import blp

blp.create_connection()
```

- For functions, wrapper function is recommended (connections will be destroyed afterwards):

```python
from xbbg import blp

@blp.with_bloomberg
def query_bbg():
    """
    All queries share the same connection
    """
    blp.bdp(...)
    blp.bdh(...)
    blp.bdib(...)
```

### Data Storage

If `BBG_ROOT` is provided in `os.environ`, data can be saved locally.
By default, local storage is preferred than Bloomberg for all queries.

Noted that local data usage must be compliant with Bloomberg Datafeed Addendum
(full description in `DAPI<GO>`):

> To access Bloomberg data via the API (and use that data in Microsoft Excel), 
> your company must sign the 'Datafeed Addendum' to the Bloomberg Agreement. 
> This legally binding contract describes the terms and conditions of your use 
> of the data and information available via the API (the "Data"). 
> The most fundamental requirement regarding your use of Data is that it cannot 
> leave the local PC you use to access the BLOOMBERG PROFESSIONAL service.
