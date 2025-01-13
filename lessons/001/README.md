# 做个Agent控制我的Mac


## 需求描述

我在录视频的时候，需要进行一些桌面的设置操作，比如隐藏顶部菜单栏，隐藏 dock(程序坞)，修改屏幕分辨率等等。这些操作都是重复的，而且比较繁琐，我希望能够通过语音或文字输入的方式，让我的Mac电脑自动完成这些操作。

因此创建了一个 Agent，比如当我输入：`进入演示模式`，agent 会帮我执行: 隐藏顶部菜单栏，隐藏 dock，修改屏幕分辨率，进入第二桌面等操作，方便我做演示，录视频。

## Agent 工具

| 工具名称 | 控制功能 | 文字输入示例 |
| --- | --- | --- |
| hide_top_menu_bar | 控制顶部菜单栏显示或隐藏 | 请显示顶部菜单，请关闭顶部菜单 |
| open_app | 打开应用程序 | 请打开浏览器 |
| hide_dock | 控制 dock 显示活隐藏 | 请显示 dock |
| move_dock | 控制 dock显示位置 | 请把 dock 显示在右边 |
| change_system_mode | 修改系统模式(演示/正常) | 进入演示模式, 退出演示模式 |


## 创建和运行项目

安装 `uv` 工具
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

创建项目
```bash
# Create a new directory for our project
uv init mac-agent
cd mac-agent

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add openai "mcp[cli]"
```

创建 `agent.py`和`server.py` 文件， 并添加代码。

运行项目
```bash
python agent.py
```
首次运行需要同意访问权限， 请点击 `允许`。

## 其他依赖

项目中的修改屏幕分辨率功能需要安装 `displayplacer` 依赖，可以通过以下命令安装：
```bash
brew install displayplacer
```
同时具体的显示分辨率参数可以通过 `displayplacer list` 命令查看，并在代码里面修改演示模式的参数。

