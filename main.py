import time
import pymysql
from datetime import datetime
from longport.openapi import Config, QuoteContext
from longport.openapi import SubType
from longport.openapi import PushQuote, PushTrades, PushDepth
from config import SYMBOL
from dotenv import load_dotenv
import os
import logging
import queue
import threading

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建数据队列
quote_queue = queue.Queue()

# 加载环境变量
load_dotenv()
logger.info("环境变量加载完成")

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'db': os.getenv('DB_NAME', 'trading_data'),
    'charset': 'utf8mb4',
    'connect_timeout': 10,  # 连接超时时间（秒）
    'read_timeout': 10,     # 读取超时时间（秒）
    'write_timeout': 10,    # 写入超时时间（秒）
    'autocommit': True      # 自动提交事务
}

logger.info(
    f"数据库配置: host={DB_CONFIG['host']}, user={DB_CONFIG['user']}, db={DB_CONFIG['db']}")


# 初始化数据库连接
def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        logger.error("错误详情:", exc_info=True)
        raise


def save_quote_data(symbol: str, event: PushQuote):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO t_quotes (
                stock_code, last_done, open, high, low, volume, turnover,
                trade_status, current_volume, current_turnover, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                symbol, event.last_done, event.open, event.high, event.low,
                event.volume, event.turnover, event.trade_status,
                event.current_volume, event.current_turnover, datetime.now()
            ))
        conn.commit()
    except Exception as e:
        logger.error(f"保存行情数据失败: {e}")
        logger.error(f"错误详情: {str(e)}", exc_info=True)
    finally:
        try:
            conn.close()
        except:
            logger.warning("关闭数据库连接时发生错误")


def database_worker():
    while True:
        try:
            # 从队列获取数据，设置超时时间
            data = quote_queue.get(timeout=1)
            if data is None:  # 用于优雅退出
                break
            symbol, event = data
            save_quote_data(symbol, event)
            quote_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"数据库工作线程错误: {e}")


def on_quote(symbol: str, event: PushQuote):
    try:
        # 将数据放入队列，不阻塞
        quote_queue.put((symbol, event), block=False)
    except queue.Full:
        logger.warning("队列已满，丢弃数据")
    except Exception as e:
        logger.error(f"处理行情数据失败: {e}")


# 启动数据库工作线程
db_thread = threading.Thread(target=database_worker, daemon=True)
db_thread.start()

config = Config.from_env()
quote_ctx = QuoteContext(config)


def on_trades(symbol: str, event: PushTrades):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO t_trades (
                stock_code, price, volume, trade_type, direction,
                 timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            for trade in event.trades:
                cursor.execute(sql, (
                    symbol, trade.price, trade.volume, trade.trade_type,
                    trade.direction, datetime.now()
                ))
        conn.commit()
    except Exception as e:
        print(f"Error saving trade data: {e}")
    finally:
        conn.close()


def on_depth(symbol: str, event: PushDepth):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 插入新的盘口数据
            sql = """
            INSERT INTO t_depths (
                stock_code, position, price, volume, order_num, type
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """

            # 处理卖盘
            for ask in event.asks:
                cursor.execute(sql, (
                    symbol, ask.position, ask.price, ask.volume,
                    ask.order_num, 'ask'
                ))

            # 处理买盘
            for bid in event.bids:
                cursor.execute(sql, (
                    symbol, bid.position, bid.price, bid.volume,
                    bid.order_num, 'bid'
                ))
        conn.commit()
    except Exception as e:
        print(f"Error saving depth data: {e}")
    finally:
        conn.close()


# 订阅实时价格
quote_ctx.set_on_quote(on_quote)
quote_ctx.subscribe([SYMBOL], [SubType.Quote], is_first_push=True)

# 订阅实时成交
quote_ctx.set_on_trades(on_trades)
quote_ctx.subscribe([SYMBOL], [SubType.Trade], is_first_push=True)

# 订阅实时盘口
quote_ctx.set_on_depth(on_depth)
quote_ctx.subscribe([SYMBOL], [SubType.Depth], is_first_push=True)

print(f"服务启动成功，当前时间为北京时间: {datetime.now()}")
logger.info("开始运行主循环")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("程序被用户中断")
    # 通知数据库线程退出
    quote_queue.put(None)
    db_thread.join()
except Exception as e:
    logger.error(f"程序运行出错: {e}")
    quote_queue.put(None)
    db_thread.join()
