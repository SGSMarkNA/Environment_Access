import os
from Environment_Access import utilities, System_Paths

# Get The Current Users Name
CURRENT_USER_NAME = os.environ.get("USERNAME", None)
# Setting Used To Tell Wings IDE Weather Or Not To Load wingdbstub
USE_WING_DEBUG = int(utilities.get_and_set_environ_key("USE_WING_DEBUG", default="0", force_default=False))
# Setting Used To Tell The Softwares That Use It Weather Or Not To Load Costum User Tools
NO_USER_TOOLS  = int(utilities.get_and_set_environ_key("NO_USER_TOOLS", default="0", force_default=False))


SHOTGUN_USER_NAMES          = utilities.path_Builder(System_Paths._CODE_SETTINGS_AND_PREFS, "Shotgun_User_Names.json")
LIGHTMAP_LICENSES           = utilities.path_Builder(System_Paths._CODE_SETTINGS_AND_PREFS, "lightmap", "5", "licenses")
ICC_FILES                   = utilities.path_Builder(System_Paths._CODE_NUKE, "ICC_Profiles")
LUT_FILES                   = utilities.path_Builder(System_Paths._CODE_NUKE, "LUTs")
LIGHTMAP_PRESETS            = utilities.path_Builder(System_Paths._CODE_SETTINGS_AND_PREFS, "lightmap", "5", "presets")
GLOBAL_WPYTHON_EXE          = utilities.path_Builder(System_Paths._CODE_PYTHON_27, "pythonw.exe")
GLOBAL_PYTHON_EXE           = utilities.path_Builder(System_Paths._CODE_PYTHON_27, "python.exe")
AWPYEXE_ICON                = utilities.path_Builder(System_Paths._CODE_PYTHON_27, "DLLs", "awpyexe.ico")
SHOTGUN_ACTION_MENU_HANDLER = utilities.path_Builder(System_Paths._CODE_SHOTGUN, "Shotgun_ActionMenu_Items", "action_handler.py")
RV_EXE                      = utilities.path_Builder(System_Paths._CODE_RV, "7.1.2", "bin", "rv.exe")
AW_SYSTEM_TRAY_EXE          = utilities.path_Builder(System_Paths._CODE_COMMAND_LINE_APPS, "System_Tray", "systray.awpyexe")
EXIF_TOOL                   = utilities.path_Builder(System_Paths._CODE_COMMAND_LINE_APPS, "exiftool.exe")
OCIO_CONFIG_FILE			= utilities.path_Builder(System_Paths._CONFIG_OCIO, "aw_Comp_aces_1.0.3", "aw_Comp_config.ocio")
