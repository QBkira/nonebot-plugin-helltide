from nonebot import require, Bot, get_driver
from nonebot.plugin import PluginMetadata
import nonebot
import httpx
from .config import Config
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
)
import datetime

__plugin_meta__ = PluginMetadata(
    name="helltide",
    description="一个Diablo4的helltide和世界boss的提醒小助手",
    # BEGIN: 7d7f3c7b5d4a
    usage="这是一个diablo4插件，可以订阅游戏中的事件，如boss刷新、地狱潮汐等，\n当事件即将发生时会自动提醒订阅用户。使用方法：\n1. 订阅事件：d4订阅 boss/helltide\n2. 取消订阅事件：d4取消订阅 boss/helltide\n3. 查询订阅列表：d4查询订阅",
    # END: 7d7f3c7b5d4a
    homepage="https://github.com/QBkira/nonebot-plugin-helltide",
    type="library",
    config=Config,
    extra={"author": "qbkira"},
)

my_config = Config.parse_obj(get_driver().config)

import json
import os
from pathlib import Path
import aiofiles
from typing import Dict, List

data_path = Path("data/diablo4").resolve() / "data.json"


subscription_dict = {}

def load_data():
    print(f"load_data path: {data_path}")
    if not os.path.exists(data_path.parent):
        os.makedirs(data_path.parent)
    if os.path.exists(data_path):
        with open(data_path, mode='r') as f:
            subscription_dict = json.loads(f.read())
    else:
        subscription_dict = {}
        with open(data_path, mode='w') as f:
            f.write(json.dumps(subscription_dict))
    print(f"订阅用户：{subscription_dict}")
    return subscription_dict
    
async def save_data():
    async with aiofiles.open(data_path, mode='w') as f:
        await f.write(json.dumps(subscription_dict))
        
subscription_dict = load_data()

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


# Add a dictionary to store the notice status of each event
notice_status = {}

@scheduler.scheduled_job("interval", minutes=my_config.event_check_interval)
async def check_event():
    url = my_config.url_api
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = parse_event_data(response)
            for group_id in subscription_dict:
                subscription_list = subscription_dict[group_id]
                if group_id not in notice_status:
                    notice_status[group_id] = {
                        "boss": False,
                        "helltide": False
                    }
                if subscription_list:
                    if data["boss"]["expected"] - datetime.datetime.now().timestamp() <= 600:
                        if not notice_status[group_id]["boss"]:
                            await boss_notice_subscription_users(group_id, data)
                            notice_status[group_id]["boss"] = True
                    else:
                        notice_status[group_id]["boss"] = False
                    if data["helltide"]["expected"] - datetime.datetime.now().timestamp() <= 600:
                        if not notice_status[group_id]["helltide"]:
                            await helltide_notice_subscription_users(group_id, data)
                            notice_status[group_id]["helltide"] = True
                    else:
                        notice_status[group_id]["helltide"] = False
    except Exception as e:
        print(f"Error occurred while checking event: {e}")

# Add command to query current subscribed users
d4_query_subscriptions = on_command("d4查询订阅", aliases={"d4query"}, block=True, rule=to_me(), priority=1)

@d4_query_subscriptions.handle()
async def query_subscriptions_handler(bot: Bot, event: MessageEvent):
    group_id = str(event.group_id)
    print(f"subscription_dict: {subscription_dict}")
    if group_id not in subscription_dict:
        subscription_dict[group_id] = []
    subscription_list = subscription_dict[group_id]
    if not subscription_list:
        await bot.send(event, "当前没有用户订阅 Diablo4 定时消息提醒。\n使用[@机器人 d4订阅] 可以订阅 Diablo4 定时消息提醒。")
    else:
        subscribed_users = "\n".join([f"{i+1}. {user_id}" for i, user_id in enumerate(subscription_list)])
        await bot.send(event, f"当前订阅 Diablo4 定时消息提醒的用户有：\n{subscribed_users}\n使用[@机器人 d4订阅] 可以订阅 Diablo4 定时消息提醒。")

d4_subscribe = on_command("d4订阅", aliases={"d4sub"}, block=True, rule=to_me(), priority=1)

@d4_subscribe.handle()
async def subscribe_handler(bot: Bot, event: MessageEvent):
    group_id = str(event.group_id)
    user_id = event.user_id
    if group_id not in subscription_dict:
        subscription_dict[group_id] = []
    subscription_list = subscription_dict[group_id]
    if user_id not in subscription_list:
        subscription_list.append(user_id)
        subscription_dict[group_id] = subscription_list
        await save_data()
        await bot.send(event, "订阅成功！\n使用[@机器人 d4取消订阅] 可以取消订阅 Diablo4 定时消息提醒。")
    else:
        await bot.send(event, "您已经订阅了 Diablo4 定时消息提醒。\n使用[@机器人 d4取消订阅] 可以取消订阅 Diablo4 定时消息提醒。")

d4_unsubscribe = on_command("d4取消订阅", aliases={"d4unsub"}, block=True, rule=to_me(), priority=1)

@d4_unsubscribe.handle()
async def unsubscribe_handler(bot: Bot, event: MessageEvent):
    group_id = str(event.group_id)
    user_id = event.user_id
    if group_id not in subscription_dict:
        subscription_dict[group_id] = []
    subscription_list = subscription_dict[group_id]
    if user_id in subscription_list:
        subscription_list.remove(user_id)
        subscription_dict[group_id] = subscription_list
        await save_data()
        await bot.send(event, "取消订阅成功！\n使用[@机器人 d4订阅] 可以订阅 Diablo4 定时消息提醒。")
    else:
        await bot.send(event, "您还没有订阅 Diablo4 定时消息提醒。\n使用[@机器人 d4订阅] 可以订阅 Diablo4 定时消息提醒。")

d4armory = on_command("diablo4", aliases={"d4"}, block=True, rule=to_me(), priority=1)

@d4armory.handle()
async def diablo4(event: MessageEvent) -> None:
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        if group_id not in subscription_dict:
            subscription_dict[group_id] = []
        subscription_list = subscription_dict[group_id]
        result = await response_event_info()
        if subscription_list:
            at_users = " ".join([f"[CQ:at,qq={user_id}]" for user_id in subscription_list])
            result = f"{result}\n\n{at_users}"
        await d4armory.send(result)
    else:
        result = await response_event_info()
        await d4armory.send(result)

async def response_event_info():
    try:
        url = my_config.url_api
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = parse_event_data(response)
            return parse_event_info(data)
    except Exception as e:
        print(f"Error occurred while fetching event info: {e}")
        return "无法获取 Diablo4 事件信息，请稍后再试。"

async def helltide_notice_subscription_users(group_id, data):
    bot = nonebot.get_bot()
    info = parse_event_info(data)
    subscription_list = subscription_dict[group_id]
    if subscription_list:
        at_users = " ".join([f"[CQ:at,qq={user_id}]" for user_id in subscription_list])
        message = f"{info}\n\n{at_users}\n[地狱狂潮]刷新时间还差不到10分钟，请做好准备！\n使用[@机器人 d4订阅] 可以订阅定时消息提醒。"
        await bot.send_group_msg(group_id=group_id, message=message)

                
async def boss_notice_subscription_users(group_id, data):
    bot = nonebot.get_bot()
    info = parse_event_info(data)
    subscription_list = subscription_dict[group_id]
    if subscription_list:
        at_users = " ".join([f"[CQ:at,qq={user_id}]" for user_id in subscription_list])
        message = f"{info}\n\n{at_users}\n[Boss]刷新时间还差不到10分钟，请做好准备！\n使用[@机器人 d4订阅] 可以订阅定时消息提醒。"
        await bot.send_group_msg(group_id=group_id, message=message)


def parse_event_data(response):
    data = response.json()
    helltide = data["helltide"]
    helltide["expected"] = helltide["timestamp"] + 2*60*60 + 15*60 # Add expected attribute to helltide
    return data

def parse_event_info(data):
    boss = data["boss"]
    helltide = data["helltide"]
    legion = data["legion"]
    now = datetime.datetime.now().timestamp()
    boss_expected_name = boss["expectedName"]
    boss_expected_timestamp = datetime.datetime.fromtimestamp(boss["expected"]).strftime('%Y-%m-%d %H:%M:%S')
    if now - helltide["timestamp"] <= 3600:
        helltide_expected = datetime.datetime.fromtimestamp(helltide["timestamp"] + 3600).strftime('%Y-%m-%d %H:%M:%S')
        result = f"Boss名字: {boss_expected_name}\nBoss刷新: {boss_expected_timestamp}\n狂潮(中): {helltide_expected}结束\n军团时间: {datetime.datetime.fromtimestamp(legion['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        result = f"Boss名字: {boss_expected_name}\nBoss刷新: {boss_expected_timestamp}\n狂潮刷新: {datetime.datetime.fromtimestamp(helltide['expected']).strftime('%Y-%m-%d %H:%M:%S')}\n军团时间: {datetime.datetime.fromtimestamp(legion['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
    return result

# Add command to trigger event check for debugging purposes
d4_debug = on_command("d4调试", aliases={"d4debug"}, block=True, rule=to_me(), priority=1)

@d4_debug.handle()
async def debug_handler(bot: nonebot.Bot, event: MessageEvent):
    url = "https://d4armory.io/api/events/recent"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        group_id = str(event.group_id)
        data = parse_event_data(response)
        await boss_notice_subscription_users(group_id, data)
        await helltide_notice_subscription_users(group_id, data)

# Add command to display help information
d4_help = on_command("d4帮助", aliases={"d4help"}, block=True, rule=to_me(), priority=1)

### 指令表
# | 指令 | 权限 | 需要@ | 范围 | 说明 |
# |:-----:|:----:|:----:|:----:|:----:|
# | [@机器人 d4] | 群员 | 是 | 群聊 | 查询 Diablo4 事件信息 |
# | [@机器人 d4订阅] | 群员 | 是 | 群聊 | 订阅 Diablo4 定时消息提醒 |
# | [@机器人 d4取消订阅] | 群员 | 是 | 群聊 | 取消订阅 Diablo4 定时消息提醒 |
# | [@机器人 d4查询订阅] | 群员 | 是 | 群聊 | 查询当前订阅 Diablo4 定时消息提醒的用户 |
# | [@机器人 d4帮助] | 群员 | 是 | 群聊 | 显示帮助信息 |
@d4_help.handle()
async def help_handler(bot: nonebot.Bot, event: MessageEvent):
    help_info = "以下是 Diablo4 定时消息提醒机器人的指令说明：\n\n"
    help_info += "[@机器人 d4] - 查询 Diablo4 事件信息\n"
    help_info += "[@机器人 d4订阅] - 订阅 Diablo4 定时消息提醒\n"
    help_info += "[@机器人 d4取消订阅] - 取消订阅 Diablo4 定时消息提醒\n"
    help_info += "[@机器人 d4查询订阅] - 查询当前订阅 Diablo4 定时消息提醒的用户\n"
    help_info += "[@机器人 d4帮助] - 显示帮助信息\n"
    # help_info += "[@机器人 d4调试] - 触发事件检查以进行调试\n"
    await bot.send(event, help_info)
