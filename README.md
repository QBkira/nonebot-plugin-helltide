<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-helltide

_✨ 一个Diablo4的helltide和世界boss的提醒小助手 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/qbkira/nonebot-plugin-helltide.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-helltide">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-helltide.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

添加机器人到群聊中，订阅之后在群里会提醒订阅Boss刷新，地狱狂潮提醒，（还有军团的刷新时间）

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-helltide

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-helltide
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-helltide
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-helltide
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-helltide
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_helltide"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| event_check_interval | 否 | 1 | 每隔1分钟检查一下 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| d4 | 群员 | 是 | 群聊 | 查询 Diablo4 事件信息 |
| d4订阅 | 群员 | 是 | 群聊 | 订阅 Diablo4 定时消息提醒 |
| d4取消订阅 | 群员 | 是 | 群聊 | 取消订阅 Diablo4 定时消息提醒 |
| d4查询订阅 | 群员 | 是 | 群聊 | 查询当前订阅 Diablo4 定时消息提醒的用户 |
| d4帮助 | 群员 | 是 | 群聊 | 显示帮助信息 |
