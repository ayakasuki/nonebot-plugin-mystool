"""
### 米游社商品兑换前端以及计划任务相关
"""
import asyncio
import io
import os
import threading
import time
<<<<<<< HEAD
from datetime import datetime
from multiprocessing import Manager
from multiprocessing.pool import Pool
from multiprocessing.synchronize import Lock
from typing import List, Union, Callable, Any, Tuple, Optional, Dict

import nonebot
from apscheduler.events import JobExecutionEvent, EVENT_JOB_EXECUTED
from nonebot import on_command, get_bot
from nonebot.adapters.onebot.v11 import (MessageEvent, MessageSegment,
                                         PrivateMessageEvent, GroupMessageEvent)
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgStr, ArgPlainText, T_State, CommandArg, Command
from nonebot_plugin_apscheduler import scheduler

from .data_model import Good, GameRecord, ExchangeStatus
from .good_image import game_list_to_image
from .plugin_data import PluginDataManager, write_plugin_data
from .simple_api import get_game_record, get_good_detail, get_good_list, good_exchange_sync
from .user_data import UserAccount, ExchangePlan, ExchangeResult
from .utils import NtpTime, COMMAND_BEGIN, logger, get_last_command_sep

_conf = PluginDataManager.plugin_data_obj
_driver = nonebot.get_driver()

myb_exchange_plan = on_command(f"{_conf.preference.command_start}兑换",
                               aliases={(f"{_conf.preference.command_start}兑换", "+"),
                                        (f"{_conf.preference.command_start}兑换", "-")},
                               priority=5, block=True)
myb_exchange_plan.name = "兑换"
myb_exchange_plan.usage = "跟随指引，配置米游币商品自动兑换计划。添加计划之前，请先前往米游社设置好收货地址，" \
                          "并使用『{HEAD}地址』选择你要使用的地址。" \
                          "所需的商品ID可通过命令『{HEAD}商品』获取。" \
                          "注意，不限兑换时间的商品将不会在此处显示。 "
myb_exchange_plan.extra_usage = """\
具体用法：
{HEAD}兑换{SEP}+ <商品ID> ➢ 新增兑换计划
{HEAD}兑换{SEP}- <商品ID> ➢ 删除兑换计划
{HEAD}商品 ➢ 查看米游社商品
『{SEP}』为分隔符，使用NoneBot配置中的其他分隔符亦可\
"""
=======
import traceback
import zipfile
from multiprocessing import Lock
from typing import List, Literal, NewType, Tuple, Union, Optional

import httpx
import tenacity
from PIL import Image, ImageDraw, ImageFont

from .bbsAPI import GameRecord, get_game_record
from .config import PATH
from .config import config as conf
from .data import UserAccount
from .utils import (check_login, custom_attempt_times, generate_device_id,
                    get_file, logger)

URL_GOOD_LIST = "https://api-takumi.mihoyo.com/mall/v1/web/goods/list?app_id=1&point_sn=myb&page_size=20&page={" \
                "page}&game={game} "
URL_CHECK_GOOD = "https://api-takumi.mihoyo.com/mall/v1/web/goods/detail?app_id=1&point_sn=myb&goods_id={}"
URL_EXCHANGE = "https://api-takumi.mihoyo.com/mall/v1/web/goods/exchange"
HEADERS_GOOD_LIST = {
    "Host":
        "api-takumi.mihoyo.com",
    "Accept":
        "application/json, text/plain, */*",
    "Origin":
        "https://user.mihoyo.com",
    "Connection":
        "keep-alive",
    "x-rpc-device_id": generate_device_id(),
    "x-rpc-client_type":
        "5",
    "User-Agent":
        conf.device.USER_AGENT_MOBILE,
    "Referer":
        "https://user.mihoyo.com/",
    "Accept-Language":
        "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding":
        "gzip, deflate, br"
}
HEADERS_EXCHANGE = {
    "Accept":
        "application/json, text/plain, */*",
    "Accept-Encoding":
        "gzip, deflate, br",
    "Accept-Language":
        "zh-CN,zh-Hans;q=0.9",
    "Connection":
        "keep-alive",
    "Content-Type":
        "application/json;charset=utf-8",
    "Host":
        "api-takumi.mihoyo.com",
    "User-Agent":
        conf.device.USER_AGENT_MOBILE,
    "x-rpc-app_version":
        conf.device.X_RPC_APP_VERSION,
    "x-rpc-channel":
        "appstore",
    "x-rpc-client_type":
        "1",
    "x-rpc-device_id": None,
    "x-rpc-device_model":
        conf.device.X_RPC_DEVICE_MODEL_MOBILE,
    "x-rpc-device_name":
        conf.device.X_RPC_DEVICE_NAME_MOBILE,
    "x-rpc-sys_version":
        conf.device.X_RPC_SYS_VERSION
}
FONT_URL = os.path.join(
    conf.GITHUB_PROXY, "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansHWSC.zip")
TEMP_FONT_PATH = PATH / "temp" / "font.zip"
FONT_SAVE_PATH = PATH / "SourceHanSansHWSC-Regular.otf"


class Good:
    """
    商品数据
>>>>>>> origin/stable


@myb_exchange_plan.handle()
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent], matcher: Matcher, state: T_State, command=Command(),
            command_arg=CommandArg()):
    """
<<<<<<< HEAD
    主命令触发
=======
    Used_Times = NewType("Used_Times", int)
    Total_Times = NewType("Total_Times", int)

    def __init__(self, good_dict: dict) -> None:
        """
        初始化商品数据

        :param good_dict: 网络请求返回的商品数据字典
        """
        self.good_dict = good_dict
        self.time_by_detail: int = -1
        try:
            for func in dir(Good):
                if func.startswith("__") and func == "async_init":
                    continue
                getattr(self, func)
        except KeyError:
            logger.error(f"{conf.LOG_HEAD}米游币商品数据 - 初始化对象: dict数据不正确")
            logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")

    async def async_init(self):
        """
        进一步异步初始化商品数据(生成商品时间Good.time)

        :return: 自身对象
        """
        if "sale_start_time" not in self.good_dict and self.good_dict["status"] == "not_in_sell":
            detail = await get_good_detail(self.good_id)
            if detail is not None:
                self.time_by_detail = detail.time
            else:
                logger.error(f"{conf.LOG_HEAD}初始化商品数据对象 - 获取商品兑换时间失败")
        return self

    @property
    def name(self) -> str:
        """
        商品名称
        """
        return self.good_dict["goods_name"]

    @property
    def good_id(self) -> str:
        """
        商品ID(Good_ID)
        """
        return self.good_dict["goods_id"]

    @property
    def price(self) -> int:
        """
        商品价格
        """
        return self.good_dict["price"]

    @property
    def time(self) -> Optional[int]:
        """
        兑换时间
        """
        # "next_time" 为 0 表示任何时间均可兑换或兑换已结束
        # "type" 为 1 时商品只有在指定时间开放兑换；为 0 时商品任何时间均可兑换
        if self.good_dict["type"] != 1 and self.good_dict["next_time"] == 0:
            return None
        elif self.good_dict["status"] == "not_in_sell" and "sale_start_time" in self.good_dict:
            return int(self.good_dict["sale_start_time"])
        else:
            return self.good_dict["next_time"]

    @property
    def num(self) -> Union[None, int]:
        """
        库存
        """
        if self.good_dict["type"] != 1 and self.good_dict["next_num"] == 0:
            return None
        else:
            return self.good_dict["next_num"]

    @property
    def limit(self) -> Tuple[Used_Times, Total_Times, Literal["forever", "month"]]:
        """
        限购，返回元组 (已经兑换次数, 最多可兑换次数, 限购类型)
        """
        return (self.good_dict["account_exchange_num"],
                self.good_dict["account_cycle_limit"], self.good_dict["account_cycle_type"])

    @property
    def icon(self) -> str:
        """
        商品图片链接
        """
        return self.good_dict["icon"]

    @property
    def is_visual(self) -> bool:
        """
        是否为虚拟商品
        """
        if self.good_dict["type"] == 2:
            return True
        else:
            return False

>>>>>>> origin/stable

    :command: 主命令和二级命令的元组
    :command_arg: 二级命令的参数，即商品ID，为Message
    """
    if command_arg and len(command) == 1:
        # 如果没有二级命令，但是有参数，则说明用户没有意向使用本功能。
        # 例如：/兑换码获取，识别到的参数为"码获取"，而用户可能有意使用其他插件。
        await matcher.finish()
    elif len(command) > 1 and command[1] in ["+", "-"]:
        if not command_arg:
            await matcher.reject(
                '⚠️您的输入有误，缺少商品ID，请重新输入\n\n' + matcher.extra_usage.format(HEAD=COMMAND_BEGIN,
                                                                                        SEP=get_last_command_sep()))
        elif not str(command_arg).isdigit():
            await matcher.reject(
                '⚠️商品ID必须为数字，请重新输入\n\n' + matcher.extra_usage.format(HEAD=COMMAND_BEGIN,
                                                                                 SEP=get_last_command_sep()))

    user = _conf.users.get(event.user_id)
    user_account = user.accounts if user else None
    if not user_account:
        await matcher.finish(
            f"⚠️你尚未绑定米游社账户，请先使用『{COMMAND_BEGIN}登录』进行登录")

    # 如果使用了二级命令 + - 则跳转进下一步，通过phone选择账户进行设置
    if len(command) > 1:
        state['command_2'] = command[1]
        matcher.set_arg("good_id", command_arg)
        if len(user_account) == 1:
            uid = next(iter(user_account.values())).bbs_uid
            matcher.set_arg('bbs_uid', Message(uid))
        else:
            uids = map(lambda x: x.bbs_uid, user_account.values())
            msg = "您有多个账号，您要配置以下哪个账号的兑换计划？\n"
            msg += "\n".join(map(lambda x: f"🆔{x}", uids))
            msg += "\n🚪发送“退出”即可退出"
            await matcher.send(msg)
    # 如果未使用二级命令，则进行查询操作，并结束交互
    else:
        msg = ""
        for plan in user.exchange_plans:
            good_detail_status, good = await get_good_detail(plan.good)
            if not good_detail_status:
                await matcher.finish("⚠️获取商品详情失败，请稍后再试")
            msg += f"-- 商品：{good.general_name}" \
                   f"\n- 🔢商品ID：{good.goods_id}" \
                   f"\n- 💰商品价格：{good.price} 米游币" \
                   f"\n- 📅兑换时间：{good.time_text}" \
                   f"\n- 🆔账户：{plan.account.bbs_uid}"
            msg += "\n\n"
        if not msg:
            msg = '您还没有兑换计划哦~\n\n'
        await matcher.finish(msg + matcher.extra_usage.format(HEAD=COMMAND_BEGIN, SEP=get_last_command_sep()))


@myb_exchange_plan.got('bbs_uid')
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent], matcher: Matcher, state: T_State,
            uid=ArgStr('bbs_uid')):
    """
<<<<<<< HEAD
    请求用户输入手机号以对账户设置兑换计划
=======

    try:
        async for attempt in tenacity.AsyncRetrying(stop=custom_attempt_times(retry), reraise=True,
                                                    wait=tenacity.wait_fixed(conf.SLEEP_TIME_RETRY)):
            with attempt:
                async with httpx.AsyncClient() as client:
                    res = await client.get(URL_CHECK_GOOD.format(good_id), timeout=conf.TIME_OUT)
                if res.json()['message'] == '商品不存在' or res.json()['message'] == '商品已下架':
                    return -1
                return Good(res.json()["data"])
    except KeyError or ValueError:
        logger.error(f"{conf.LOG_HEAD}米游币商品兑换 - 获取商品详细信息: 服务器没有正确返回")
        logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
        logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")
    except Exception:
        logger.error(f"{conf.LOG_HEAD}米游币商品兑换 - 获取商品详细信息: 网络请求失败")
        logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")


async def get_good_list(game: Literal["bh3", "ys", "bh2", "wd", "bbs", "xq"], retry: bool = True) -> Optional[
    List[Good]]:
>>>>>>> origin/stable
    """
    user_account = _conf.users[event.user_id].accounts
    if uid == '退出':
        await matcher.finish('🚪已成功退出')
    if uid in user_account:
        state["account"] = user_account[uid]
    else:
        await matcher.reject('⚠️您发送的账号不在以上账号内，请重新发送')


@myb_exchange_plan.got('good_id')
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent], matcher: Matcher, state: T_State,
            good_id=ArgPlainText('good_id')):
    """
    处理三级命令，即商品ID
    """
    account: UserAccount = state['account']
    command_2 = state['command_2']
    if command_2 == '+':
        good_dict = {
            'bh3': (await get_good_list('bh3'))[1],
            'ys': (await get_good_list('hk4e'))[1],
            'bh2': (await get_good_list('bh2'))[1],
            'xq': (await get_good_list('hkrpg'))[1],
            'wd': (await get_good_list('nxx'))[1],
            'bbs': (await get_good_list('bbs'))[1]
        }
        flag = True
        break_flag = False
        good = None
        for good_list in good_dict.values():
            goods_on_sell = filter(lambda x: not x.time_end and x.time_limited, good_list)
            for good in goods_on_sell:
                if good.goods_id == good_id:
                    flag = False
                    break_flag = True
                    break
            if break_flag:
                break
        if flag:
            await matcher.finish('⚠️您发送的商品ID不在可兑换的商品列表内，程序已退出')
        state['good'] = good
        if good.time:
            # 若为实物商品，也进入下一步骤，但是传入uid为None
            if good.is_virtual:
                game_records_status, records = await get_game_record(account)

                if game_records_status:
                    if len(records) == 0:
                        matcher.set_arg('uid', Message(records[0].game_role_id))
                    else:
                        msg = f'您米游社账户下的游戏账号：'
                        for record in records:
                            msg += f'\n🎮 {record.region_name} - {record.nickname} - UID {record.game_role_id}'
                        if records:
                            state['records'] = records
                            await matcher.send(
                                "您兑换的是虚拟物品，请发送想要接收奖励的游戏账号UID：\n🚪发送“退出”即可退出")
                            await asyncio.sleep(0.5)
                            await matcher.send(msg)
                        else:
                            await matcher.finish(
                                f"您的米游社账户下还没有绑定游戏账号哦，暂时不能进行兑换，请先前往米游社绑定后重试")
            else:
                if not account.address:
                    await matcher.finish('⚠️您还没有配置地址哦，请先配置地址')
                matcher.set_arg('uid', Message())
        else:
            await matcher.finish(f'⚠️该商品暂时不可以兑换，请重新设置')

    elif command_2 == '-':
        plans = _conf.users[event.user_id].exchange_plans
        if plans:
            for plan in plans:
                if plan.good.goods_id == good_id:
                    plans.remove(plan)
                    write_plugin_data()
                    for i in range(_conf.preference.exchange_thread_count):
                        scheduler.remove_job(job_id=f"exchange-plan-{hash(plan)}-{i}")
                    await matcher.finish('兑换计划删除成功')
            await matcher.finish(f"您没有设置商品ID为 {good_id} 的兑换哦~")
        else:
            await matcher.finish("您还没有配置兑换计划哦~")

    else:
        await matcher.reject(
            '⚠️您的输入有误，请重新输入\n\n' + matcher.extra_usage.format(HEAD=COMMAND_BEGIN,
                                                                         SEP=get_last_command_sep()))


@myb_exchange_plan.got('uid')
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent], matcher: Matcher, state: T_State,
            uid=ArgPlainText('uid')):
    """
    初始化商品兑换任务，如果传入UID为None则为实物商品，仍可继续
    """
    user = _conf.users[event.user_id]
    account: UserAccount = state['account']
    good: Good = state['good']
    if good.is_virtual:
        records: List[GameRecord] = state['records']
        if uid == '退出':
            await matcher.finish('🚪已成功退出')
        record_filter = filter(lambda x: x.game_role_id == uid, records)
        record = next(record_filter, None)
        if not record:
            await matcher.reject('⚠️您输入的UID不在上述账号内，请重新输入')
        plan = ExchangePlan(good=good, address=account.address, game_record=record, account=account)
    else:
        plan = ExchangePlan(good=good, address=account.address, account=account)
    if plan in user.exchange_plans:
        await matcher.finish('⚠️您已经配置过该商品的兑换哦！')
    else:
        user.exchange_plans.add(plan)
        write_plugin_data()

    # 初始化兑换任务
    finished.setdefault(plan, [])
    for i in range(_conf.preference.exchange_thread_count):
        scheduler.add_job(
            good_exchange_sync,
            "date",
            id=f"exchange-plan-{hash(plan)}-{i}",
            replace_existing=True,
            args=(plan,),
            run_date=datetime.fromtimestamp(good.time),
            max_instances=_conf.preference.exchange_thread_count
        )

    await matcher.finish(
        f'🎉设置兑换计划成功！将于 {plan.good.time_text} 开始兑换，到时将会私聊告知您兑换结果')


get_good_image = on_command(_conf.preference.command_start + '商品', priority=5, block=True)
get_good_image.name = "商品"
get_good_image.usage = "获取当日米游币商品信息。添加自动兑换计划需要商品ID，请记下您要兑换的商品的ID。"


@get_good_image.handle()
async def _(_: MessageEvent, matcher: Matcher, arg=CommandArg()):
    # 若有使用二级命令，即传入了想要查看的商品类别，则跳过询问
    if arg:
        matcher.set_arg("content", arg)


@get_good_image.got("content", prompt="请发送您要查看的商品类别:"
                                      "\n- 崩坏3"
                                      "\n- 原神"
                                      "\n- 崩坏2"
                                      "\n- 崩坏：星穹铁道"
                                      "\n- 未定事件簿"
                                      "\n- 米游社"
                                      "\n若是商品图片与米游社商品不符或报错 请发送“更新”哦~"
                                      "\n—— 🚪发送“退出”以结束")
async def _(_: MessageEvent, matcher: Matcher, arg=ArgPlainText("content")):
    """
<<<<<<< HEAD
    根据传入的商品类别，发送对应的商品列表图片
=======
    米游币商品兑换相关(需两步初始化对象，先`__init__`，后异步`async_init`)\n
    示例:
    ```python
    exchange = await Exchange(account, good_id, game_uid).async_init()
    ```

    - `result`属性为 `-1`: 用户登录失效，放弃兑换
    - `result`属性为 `-2`: 商品为游戏内物品，由于未配置stoken，放弃兑换
    - `result`属性为 `-3`: 商品为游戏内物品，由于stoken为\"v2\"类型，且未配置mid，放弃兑换
    - `result`属性为 `-4`: 暂不支持商品所属的游戏，放弃兑换
    - `result`属性为 `-5`: 获取商品的信息时，网络请求失败或服务器没有正确返回，放弃兑换
    - `result`属性为 `-6`: 获取用户游戏账户数据失败，放弃兑换
    - `result`属性为 `-7`: 实体商品，用户未配置地址ID，放弃兑换
>>>>>>> origin/stable
    """
    if arg == '退出':
        await matcher.finish('🚪已成功退出')
    elif arg in ['原神', 'ys']:
        arg = ('hk4e', '原神')
    elif arg in ['崩坏3', '崩坏三', '崩3', '崩三', '崩崩崩', '蹦蹦蹦', 'bh3']:
        arg = ('bh3', '崩坏3')
    elif arg in ['崩坏2', '崩坏二', '崩2', '崩二', '崩崩', '蹦蹦', 'bh2']:
        arg = ('bh2', '崩坏2')
    elif arg in ['崩坏：星穹铁道', '星铁', '星穹铁道', '铁道', '轨子', '星穹', 'xq']:
        arg = ('hkrpg', '崩坏：星穹铁道')
    elif arg in ['未定', '未定事件簿', 'wd']:
        arg = ('nxx', '未定事件簿')
    elif arg in ['大别野', '米游社']:
        arg = ('bbs', '米游社')
    elif arg == '更新':
        threading.Thread(target=generate_image, kwargs={"is_auto": False}).start()
        await get_good_image.finish('⏳后台正在生成商品信息图片，请稍后查询')
    else:
        await get_good_image.reject('⚠️您的输入有误，请重新输入')

    img_path = time.strftime(
        f'{_conf.good_list_image_config.SAVE_PATH}/%m-%d-{arg[0]}.jpg', time.localtime())
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            image_bytes = io.BytesIO(f.read())
        await get_good_image.finish(MessageSegment.image(image_bytes))
    else:
        await get_good_image.finish(
            f'{arg[1]} 分区暂时没有可兑换的限时商品。如果这与实际不符，你可以尝试用『{COMMAND_BEGIN}商品 更新』进行更新。')


lock = threading.Lock()
finished: Dict[ExchangePlan, List[bool]] = {}


@lambda func: scheduler.add_listener(func, EVENT_JOB_EXECUTED)
def exchange_notice(event: JobExecutionEvent):
    """
    接收兑换结果
    """
    if event.job_id.startswith("exchange-plan"):
        bot = get_bot()
        loop = asyncio.get_event_loop()

        thread_id = int(event.job_id.split('-')[-1]) + 1
        result: Tuple[ExchangeStatus, Optional[ExchangeResult]] = event.retval
        exchange_status, exchange_result = result

        if not exchange_status:
            hash_value = int(event.job_id.split('-')[-2])
            plans = map(lambda x: x.exchange_plans, _conf.users.values())
            plan_filter = filter(lambda x: hash(x[0]) == hash_value, zip(plans, _conf.users.keys()))
            plan_tuple = next(plan_filter)
            plan, user_id = plan_tuple
            with lock:
                finished[plan].append(False)
                loop.create_task(
                    bot.send_private_msg(
                        user_id=user_id,
                        message=f"⚠️账户 {plan.account.bbs_uid}"
                                f"\n- {plan.good.general_name}"
                                f"\n- 线程 {thread_id}"
                                f"\n- 兑换请求发送失败"
                    )
                )
                if len(finished[plan]) == _conf.preference.exchange_thread_count:
                    del plan
                    write_plugin_data()

        else:
            plan = exchange_result.plan
            user_filter = filter(lambda x: plan in x[1].exchange_plans, _conf.users.items())
            user_id, user = next(user_filter)
            with lock:
                # 如果已经有一个线程兑换成功，就不再接收结果
                if True not in finished[plan]:
                    if exchange_result.result:
                        finished[plan].append(True)
                        loop.create_task(
                            bot.send_private_msg(
                                user_id=user_id,
                                message=f"🎉账户 {plan.account.bbs_uid}"
                                        f"\n- {plan.good.general_name}"
                                        f"\n- 线程 {thread_id}"
                                        f"\n- 兑换成功"
                            )
                        )
                    else:
<<<<<<< HEAD
                        finished[plan].append(False)
                        loop.create_task(
                            bot.send_private_msg(
                                user_id=user_id,
                                message=f"💦账户 {plan.account.bbs_uid}"
                                        f"\n- {plan.good.general_name}"
                                        f"\n- 线程 {thread_id}"
                                        f"\n- 兑换失败"
                            )
                        )

                if len(finished[plan]) == _conf.preference.exchange_thread_count:
                    try:
                        user.exchange_plans.remove(plan)
                    except KeyError:
                        pass
                    else:
                        write_plugin_data()


@_driver.on_startup
async def _():
    """
    启动机器人时自动初始化兑换任务
    """
    for user_id, user in _conf.users.items():
        plans = user.exchange_plans
        for plan in plans:
            good_detail_status, good = await get_good_detail(plan.good)
            if good_detail_status.good_not_existed or good.time < NtpTime.time():
                # 若商品不存在则删除
                # 若重启时兑换超时则删除该兑换
                user.exchange_plans.remove(plan)
                write_plugin_data()
                continue
=======
                        if self.content["address_id"] is None:
                            logger.error(
                                f"{conf.LOG_HEAD}米游币商品兑换 - 初始化兑换任务: 商品 {self.goodID} 为实体物品，由于未配置地址ID，放弃兑换")
                            self.result = -7
                        return self

                    if good_info["game"] not in ("bh3", "hk4e", "bh2", "nxx", "hkrpg"):
                        logger.warning(
                            f"{conf.LOG_HEAD}米游币商品兑换 - 初始化兑换任务: 暂不支持商品 {self.goodID} 所属的游戏")
                        self.result = -4
                        return self

                    record_list: List[GameRecord] = await get_game_record(self.account)
                    if record_list == -1:
                        self.result = -1
                    elif isinstance(record_list, int):
                        self.result = -6

                    for record in record_list:
                        if record.uid == self.gameUID:
                            self.content.setdefault("uid", record.uid)
                            # 例: cn_gf01
                            self.content.setdefault("region", record.region)
                            # 例: hk4e_cn
                            self.content.setdefault(
                                "game_biz", good_info["game_biz"])
                            break
        except tenacity.RetryError:
            logger.error(
                f"{conf.LOG_HEAD}米游币商品兑换 - 初始化兑换任务: 获取商品 {self.goodID} 的信息失败")
            if res is not None:
                logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
            logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")
            self.result = -5
        return self

    async def start(self) -> Union[None, Tuple[bool, dict], Literal[-1, -2, -3]]:
        """
        执行兑换操作

        :return: 兑换结果 返回元组 (是否成功, 服务器返回数据)

        - 若返回 `-1` 说明用户登录失效
        - 若返回 `-2` 说明服务器没有正确返回
        - 若返回 `-3` 说明请求失败
        """
        if self.result is not None and self.result < 0:
            logger.error(f"{conf.LOG_HEAD}商品：{self.goodID} 未初始化完成，放弃兑换")
            return None
        else:
            headers = HEADERS_EXCHANGE
            headers["x-rpc-device_id"] = self.account.deviceID
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        URL_EXCHANGE, headers=headers, json=self.content, cookies=self.account.cookie,
                        timeout=conf.TIME_OUT)
                if not check_login(res.text):
                    logger.info(
                        f"{conf.LOG_HEAD}米游币商品兑换 - 执行兑换: 用户 {self.account.phone} 登录失效")
                    logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
                    return -1
                if res.json()["message"] == "OK":
                    logger.info(
                        f"{conf.LOG_HEAD}米游币商品兑换 - 执行兑换: 用户 {self.account.phone} 商品 {self.goodID} 兑换成功！可以自行确认。")
                    logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
                    return True, res.json()
                else:
                    logger.info(
                        f"{conf.LOG_HEAD}米游币商品兑换 - 执行兑换: 用户 {self.account.phone} 商品 {self.goodID} 兑换失败，可以自行确认。")
                    logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
                    return False, res.json()
            except KeyError:
                logger.error(
                    f"{conf.LOG_HEAD}米游币商品兑换 - 执行兑换: 用户 {self.account.phone} 商品 {self.goodID} 服务器没有正确返回")
                logger.debug(f"{conf.LOG_HEAD}网络请求返回: {res.text}")
                logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")
                return -2
            except Exception:
                logger.error(
                    f"{conf.LOG_HEAD}米游币商品兑换 - 执行兑换: 用户 {self.account.phone} 商品 {self.goodID} 请求失败")
                logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")
                return -3


async def game_list_to_image(good_list: List[Good], lock: Lock = None, retry: bool = True):
    """
    将商品信息列表转换为图片数据，若返回`None`说明生成失败

    :param good_list: 商品列表数据
    :param lock: 进程同步锁，防止多进程同时在下载字体
    :param retry: 是否允许重试
    """
    # TODO: 暂时会阻塞，目前还找不到更好的解决方案
    #   回调函数是否适用于 NoneBot Matcher 暂不清楚，
    #   若适用则可以传入回调函数而不阻塞主进程
    try:
        if lock is not None:
            lock.acquire()

        font_path = conf.goodListImage.FONT_PATH
        if font_path is None or not os.path.isfile(font_path):
            if os.path.isfile(FONT_SAVE_PATH):
                font_path = FONT_SAVE_PATH
            else:
                logger.warning(
                    f"{conf.LOG_HEAD}商品列表图片生成 - 缺少字体，正在从 https://github.com/adobe-fonts/source-han-sans/tree/release "
                    f"下载字体...")
                try:
                    os.makedirs(os.path.dirname(TEMP_FONT_PATH))
                except FileExistsError:
                    pass
                with open(TEMP_FONT_PATH, "wb") as f:
                    content = await get_file(FONT_URL)
                    if content is None:
                        logger.error(
                            f"{conf.LOG_HEAD}商品列表图片生成 - 字体下载失败，无法继续生成图片")
                        return None
                    f.write(content)
                with open(TEMP_FONT_PATH, "rb") as f:
                    with zipfile.ZipFile(f) as z:
                        with z.open("OTF/SimplifiedChineseHW/SourceHanSansHWSC-Regular.otf") as zip_font:
                            with open(FONT_SAVE_PATH, "wb") as fp_font:
                                fp_font.write(zip_font.read())
                logger.info(
                    f"{conf.LOG_HEAD}商品列表图片生成 - 已完成字体下载 -> {FONT_SAVE_PATH}")
                try:
                    os.remove(TEMP_FONT_PATH)
                except Exception:
                    logger.warning(
                        f"{conf.LOG_HEAD}商品列表图片生成 - 无法清理下载的字体压缩包临时文件")
                    logger.debug(f"{conf.LOG_HEAD}{traceback.format_exc()}")
                font_path = FONT_SAVE_PATH

        if lock is not None:
            lock.release()

        font = ImageFont.truetype(
            str(font_path), conf.goodListImage.FONT_SIZE, encoding=conf.ENCODING)

        size_y = 0
        '''起始粘贴位置 高'''
        position: List[tuple] = []
        '''预览图粘贴的位置'''
        imgs: List[Image.Image] = []
        '''商品预览图'''

        for good in good_list:
            async for attempt in tenacity.AsyncRetrying(stop=custom_attempt_times(retry),
                                                        wait=tenacity.wait_fixed(conf.SLEEP_TIME_RETRY)):
                with attempt:
                    async with httpx.AsyncClient() as client:
                        icon = await client.get(good.icon, timeout=conf.TIME_OUT)
            img = Image.open(io.BytesIO(icon.content))
            # 调整预览图大小
            img = img.resize(conf.goodListImage.ICON_SIZE)
            # 记录预览图粘贴位置
            position.append((0, size_y))
            # 调整下一个粘贴的位置
            size_y += conf.goodListImage.ICON_SIZE[1] + \
                      conf.goodListImage.PADDING_ICON
            imgs.append(img)

        preview = Image.new(
            'RGB', (conf.goodListImage.WIDTH, size_y), (255, 255, 255))

        i = 0
        for img in imgs:
            preview.paste(img, position[i])
            i += 1

        draw_y = conf.goodListImage.PADDING_TEXT_AND_ICON_Y
        '''写入文字的起始位置 高'''
        for good in good_list:
            draw = ImageDraw.Draw(preview)
            # 根据预览图高度来确定写入文字的位置，并调整空间
            if good.time is None:
                start_time = "不限"
>>>>>>> origin/stable
            else:
                finished.setdefault(plan, [])
                for i in range(_conf.preference.exchange_thread_count):
                    scheduler.add_job(
                        good_exchange_sync,
                        "date",
                        id=f"exchange-plan-{hash(plan)}-{i}",
                        replace_existing=True,
                        args=(plan,),
                        run_date=datetime.fromtimestamp(good.time),
                        max_instances=_conf.preference.exchange_thread_count
                    )


def image_process(game: str, lock: Lock):
    """
    生成并保存图片的进程函数

    :param game: 游戏名
    :param lock: 进程锁
    :return: 生成成功或无商品返回True，否则返回False
    """
    loop = asyncio.new_event_loop()
    good_list_status, good_list = loop.run_until_complete(get_good_list(game))
    if not good_list_status:
        logger.error(f"{_conf.preference.log_head}获取 {game} 分区的商品列表失败，跳过该分区的商品图片生成")
        return False
    good_list = list(filter(lambda x: not x.time_end and x.time_limited, good_list))
    if good_list:
        logger.info(f"{_conf.preference.log_head}正在生成 {game} 分区的商品列表图片")
        image_bytes = loop.run_until_complete(game_list_to_image(good_list, lock))
        if not image_bytes:
            return False
        date = time.strftime('%m-%d', time.localtime())
        path = _conf.good_list_image_config.SAVE_PATH / f"{date}-{game}.jpg"
        with open(path, 'wb') as f:
            f.write(image_bytes)
        logger.info(f"{_conf.preference.log_head}已完成 {game} 分区的商品列表图片生成")
    else:
        logger.info(f"{_conf.preference.log_head}{game}分区暂时没有可兑换的限时商品，跳过该分区的商品图片生成")
    return True


def generate_image(is_auto=True, callback: Callable[[bool], Any] = None):
    """
    生成米游币商品信息图片。该函数会阻塞当前线程

    :param is_auto: True为每日自动生成，False为用户手动更新
    :param callback: 回调函数，参数为生成成功与否
    """
    for root, _, files in os.walk(_conf.good_list_image_config.SAVE_PATH, topdown=False):
        for name in files:
            date = time.strftime('%m-%d', time.localtime())
            # 若图片开头为当日日期，则退出函数不执行
            if name.startswith(date):
                if is_auto:
                    return
            # 删除旧图片
            if name.endswith('.jpg'):
                os.remove(os.path.join(root, name))

    lock: Lock = Manager().Lock()
    with Pool() as pool:
        for game in "bh3", "hk4e", "bh2", "hkrpg", "nxx", "bbs":
            pool.apply_async(image_process,
                             args=(game, lock),
                             callback=callback)
        pool.close()
        pool.join()

    logger.info(f"{_conf.preference.log_head}已完成所有分区的商品列表图片生成")
