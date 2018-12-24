import pandas as pd

import os

from xbbg.core import utils, const, assist
from xbbg.io import files, logs


def hist_file(ticker: str, dt, typ='TRADE'):
    """
    Data file location for Bloomberg historical data

    Args:
        ticker: ticker name
        dt: date
        typ: [TRADE, BID, ASK, BID_BEST, ASK_BEST, BEST_BID, BEST_ASK]

    Returns:
        file location

    Examples:
        >>> os.environ['BBG_ROOT'] = ''
        >>> hist_file(ticker='ES1 Index', dt='2018-08-01') == ''
        True
        >>> os.environ['BBG_ROOT'] = '/data/bbg'
        >>> hist_file(ticker='ES1 Index', dt='2018-08-01')
        '/data/bbg/Index/ES1 Index/TRADE/2018-08-01.parq'
    """
    data_path = os.environ.get(assist.BBG_ROOT, '').replace('\\', '/')
    if not data_path: return ''
    asset = ticker.split()[-1]
    proper_ticker = ticker.replace('/', '_')
    cur_dt = pd.Timestamp(dt).strftime('%Y-%m-%d')
    return f'{data_path}/{asset}/{proper_ticker}/{typ}/{cur_dt}.parq'


def ref_file(ticker: str, fld: str, has_date=False, cache=False, ext='parq', **kwargs):
    """
    Data file location for Bloomberg reference data

    Args:
        ticker: ticker name
        fld: field
        has_date: whether add current date to data file
        cache: if has_date is True, whether to load file from latest cached
        ext: file extension
        **kwargs: other overrides passed to ref function

    Returns:
        file location

    Examples:
        >>> import shutil
        >>>
        >>> os.environ['BBG_ROOT'] = ''
        >>> ref_file('BLT LN Equity', fld='Crncy') == ''
        True
        >>> os.environ['BBG_ROOT'] = '/data/bbg'
        >>> ref_file('BLT LN Equity', fld='Crncy', cache=True)
        '/data/bbg/Equity/BLT LN Equity/Crncy/ovrd=None.parq'
        >>> ref_file('BLT LN Equity', fld='Crncy')
        ''
        >>> cur_dt = utils.cur_time(tz=utils.DEFAULT_TZ)
        >>> ref_file(
        ...     'BLT LN Equity', fld='DVD_Hist_All', has_date=True, cache=True,
        ... ).replace(cur_dt, '[cur_date]')
        '/data/bbg/Equity/BLT LN Equity/DVD_Hist_All/asof=[cur_date], ovrd=None.parq'
        >>> ref_file(
        ...     'BLT LN Equity', fld='DVD_Hist_All', has_date=True,
        ...     cache=True, DVD_Start_Dt='20180101',
        ... ).replace(cur_dt, '[cur_date]')[:-5]
        '/data/bbg/Equity/BLT LN Equity/DVD_Hist_All/asof=[cur_date], DVD_Start_Dt=20180101'
        >>> sample = 'asof=2018-11-02, DVD_Start_Dt=20180101, DVD_End_Dt=20180501.pkl'
        >>> root_path = 'xbbg/tests/data'
        >>> sub_path = f'{root_path}/Equity/AAPL US Equity/DVD_Hist_All'
        >>> os.environ['BBG_ROOT'] = root_path
        >>> for tmp_file in files.all_files(sub_path): os.remove(tmp_file)
        >>> files.create_folder(sub_path)
        >>> sample in shutil.copy(f'{root_path}/{sample}', sub_path)
        True
        >>> new_file = ref_file(
        ...     'AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20180101',
        ...     has_date=True, cache=True, ext='pkl'
        ... )
        >>> new_file.split('/')[-1] == f'asof={cur_dt}, DVD_Start_Dt=20180101.pkl'
        True
        >>> old_file = 'asof=2018-11-02, DVD_Start_Dt=20180101, DVD_End_Dt=20180501.pkl'
        >>> old_full = '/'.join(new_file.split('/')[:-1] + [old_file])
        >>> updated_file = old_full.replace('2018-11-02', cur_dt)
        >>> updated_file in shutil.copy(old_full, updated_file)
        True
        >>> exist_file = ref_file(
        ...     'AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20180101',
        ...     has_date=True, cache=True, ext='pkl'
        ... )
        >>> exist_file == updated_file
        True
    """
    data_path = os.environ.get(assist.BBG_ROOT, '').replace('\\', '/')
    if (not data_path) or (not cache): return ''

    proper_ticker = ticker.replace('/', '_')
    root = f'{data_path}/{ticker.split()[-1]}/{proper_ticker}/{fld}'

    if len(kwargs) > 0: info = utils.to_str(kwargs)[1:-1].replace('|', '_')
    else: info = 'ovrd=None'

    # Check date info
    if has_date:
        cur_dt = utils.cur_time()
        cur_files = files.all_files(path_name=root, keyword=info, ext=ext)
        missing = f'{root}/asof={cur_dt}, {info}.{ext}'
        if len(cur_files) > 0:
            upd_dt = [val for val in sorted(cur_files)[-1][:-4].split(', ') if 'asof=' in val]
            if len(upd_dt) > 0:
                diff = pd.Timestamp('today') - pd.Timestamp(upd_dt[0].split('=')[-1])
                if diff >= pd.Timedelta('10D'): return missing
            return sorted(cur_files)[-1]
        else: return missing

    else: return f'{root}/{info}.{ext}'


def save_intraday(data: pd.DataFrame, ticker: str, dt, typ='TRADE'):
    """
    Check whether data is done for the day and save

    Args:
        data: data
        ticker: ticker
        dt: date
        typ: [TRADE, BID, ASK, BID_BEST, ASK_BEST, BEST_BID, BEST_ASK]

    Examples:
        >>> os.environ['BBG_ROOT'] = 'xbbg/tests/data'
        >>> sample = pd.read_parquet('xbbg/tests/data/aapl.parq')
        >>> save_intraday(sample, 'AAPL US Equity', '2018-11-02')
        >>> # Invalid exchange
        >>> save_intraday(sample, 'AAPL XX Equity', '2018-11-02')
        >>> # Invalid empty data
        >>> save_intraday(pd.DataFrame(), 'AAPL US Equity', '2018-11-02')
        >>> # Invalid date - too close
        >>> cur_dt = utils.cur_time()
        >>> save_intraday(sample, 'AAPL US Equity', cur_dt)
    """
    cur_dt = pd.Timestamp(dt).strftime('%Y-%m-%d')
    logger = logs.get_logger(save_intraday, level='debug')
    info = f'{ticker} / {cur_dt} / {typ}'
    data_file = hist_file(ticker=ticker, dt=dt, typ=typ)
    if not data_file: return

    if data.empty:
        logger.warning(f'data is empty for {info} ...')
        return

    exch = const.exch_info(ticker=ticker)
    if exch.empty: return

    end_time = pd.Timestamp(
        const.market_timing(ticker=ticker, dt=dt, timing='FINISHED')
    ).tz_localize(exch.tz)
    now = pd.Timestamp('now', tz=exch.tz) - pd.Timedelta('1H')

    if end_time > now:
        logger.debug(f'skip saving cause market close ({end_time}) < now - 1H ({now}) ...')
        return

    logger.info(f'saving data to {data_file} ...')
    files.create_folder(data_file, is_file=True)
    data.to_parquet(data_file)
