# server.py
import os
import subprocess
from mcp.server.fastmcp import FastMCP, Context

# Create an MCP server
mcp = FastMCP("Mac Server")

@mcp.tool(
    name="open_app",
    description="Open an application on MacOS",
)
def open_app(name: str):
    result = subprocess.run(["open", "-a", name], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Error: {result.stderr}")

@mcp.tool(
    name="close_app",
    description="Close an application on MacOS",
)
def close_app(name: str):
    os.system(f"killall \"{name}\"")

# top menu bar visibility tool
@mcp.tool(
    name="hide_top_menu_bar",
    description="Hide or show the top menu bar on MacOS",
)
def hide_top_menu_bar(hide: bool):
    os.system(f"osascript -e 'tell application \"System Events\" to set autohide menu bar of dock preferences to {str(hide).lower()}'")
    return

# dock visibility tool
@mcp.tool(
    name="hide_dock",
    description="Hide or show the dock on MacOS",
)
def hide_dock(hide: bool):
    os.system(f"osascript -e 'tell application \"System Events\" to set autohide of dock preferences to {str(hide).lower()}'")
    return

# dock position tool
@mcp.tool(
    name="move_dock",
    description="Move the dock to left or right or bottom",
)
def move_dock(position: str):
    os.system(f"defaults write com.apple.dock orientation {position} && killall Dock")
    return


# system mode tool
@mcp.tool(
    name="change_system_mode",
    description="Change system mode to presenter or normal",
)
def change_system_mode(mode: str):
    hide_dock(mode == "presenter")
    hide_top_menu_bar(mode == "presenter")
    set_screen_resolutions(mode == "presenter")
    if mode == "presenter":
        switch_to_desktop_2()
    return

def set_screen_resolutions(presenter_mode: bool):
    try:
        # get screen id from command `displayplacer list`
        result = subprocess.check_output(["displayplacer", "list"]).decode("utf-8")
        first_line = result.split("\n")[0]
        screen_id = first_line.split(":")[1].strip()

        # normal mode: 67, presenter mode: 50
        mode = 67
        if presenter_mode:
            mode = 50

        cmd_arg = f"id:{screen_id} mode:{mode}"
        # logging.info(f"Setting screen resolution: {cmd_arg}")
        subprocess.check_output(["displayplacer", cmd_arg])
    except subprocess.CalledProcessError as e:
        # logging.error(f"Error setting screen resolution: {e}")
        return e
    return None

def switch_to_desktop_2():
    applescript = '''
    tell application "System Events"
        key code 19 using {control down}
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
    except subprocess.CalledProcessError as e:
        return e
    return None    

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')    