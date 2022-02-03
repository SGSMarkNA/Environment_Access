import os
import subprocess
from Environment_Access import utilities

__this_dir = os.path.dirname(__file__)

# Master Code Location Paths
if os.name == 'nt':
	_CODE_BASE               = utilities.path_fixer(os.path.realpath(__this_dir+"/../.."))
	_APPS_BASE               = utilities.path_fixer(os.path.realpath(__this_dir+"/../../../Apps"))
	_PIPE_BASE               = utilities.path_fixer(os.path.realpath(__this_dir+"/../../../Pipeline"))
	_COMMON_BASE             = utilities.path_fixer(os.path.realpath("V:"))
	_LIBRARY_BASE             = utilities.path_fixer(os.path.realpath("W:"))
elif os.name == 'posix':
	_CODE_BASE               = utilities.path_fixer("/Volumes/aw_config/Git_Live_Code")
	_APPS_BASE               = utilities.path_fixer(os.path.realpath("/Volumes/aw_config/Apps"))
	_PIPE_BASE               = utilities.path_fixer(os.path.realpath("/Volumes/aw_config/Pipeline"))
	_COMMON_BASE             = utilities.path_fixer(os.path.realpath("/Volumes/common"))
	_LIBRARY_BASE             = utilities.path_fixer(os.path.realpath("/Volumes/library"))

_EXT_API_SHOTGUN_SGTK    = utilities.path_Builder(_PIPE_BASE, "Shotgun", "studio", "install", "core", "python")

_CODE_COMMON_UTILITIES   = utilities.path_Builder(_COMMON_BASE, "Utilities") 
# _CODE_BASE             = r"C:\Users\dloveridge\Documents\AW_Git_New_Storage_Repos"

# Top Level Code Location Paths
_CODE_GLOBAL_SYSTEMS     = utilities.path_Builder(_CODE_BASE, "Global_Systems")
_CODE_SOFTWARE           = utilities.path_Builder(_CODE_BASE, "Software")
_CODE_SGTK               = utilities.path_Builder(_CODE_BASE, "SGTK")
# PIPLINE Code Location Paths
# Global Systems Code Location Paths
_CODE_SETTINGS_AND_PREFS = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "Settings_And_Prefs")
_CODE_ENVIRONMENT_ACCESS = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "Environment_Access")
_CODE_AW_SITE_PACKAGES   = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "AW_site_packages")
_CODE_COMMAND_LINE_APPS  = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "Command_Line_Apps")
_CODE_AW_USER_TOOLS      = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "User_Tools")
_CODE_QT                 = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "QT")
_CODE_DEADLINE_SCRIPT_EXECUTE  = utilities.path_Builder(_CODE_GLOBAL_SYSTEMS, "Deadline_Script_Execute")

# Application Location Paths
_CODE_PYTHON             = utilities.path_Builder(_APPS_BASE, "Python")
_CODE_PYTHON_27          = utilities.path_Builder(_CODE_PYTHON, "Python27")
_CODE_RV                 = utilities.path_Builder(_APPS_BASE, "RV")

# Software Code Location Paths
_CODE_DEADLINE       = utilities.path_Builder(_CODE_SOFTWARE, "Deadline")
_CODE_SHOTGUN        = utilities.path_Builder(_CODE_SOFTWARE, "Shotgun")

# Common Config Location Paths
_CONFIG_OCIO          = utilities.path_Builder(_LIBRARY_BASE, "OCIO_Configs")

# Maya Paths
_CODE_MAYA                         = utilities.path_Builder(_CODE_SOFTWARE, "Maya")
_CODE_MAYA_SCRIPT_PATH             = utilities.path_Builder(_CODE_MAYA, "Mel")
_CODE_MAYA_SCRIPT_PATH_2015        = utilities.path_Builder(_CODE_MAYA_SCRIPT_PATH, "2015")
_CODE_MAYA_PLUGINS                 = utilities.path_Builder(_CODE_MAYA, "plug-ins")
_CODE_MAYA_USER_TOOLS              = utilities.path_Builder(_CODE_AW_USER_TOOLS, "Maya_User_Tools")
_CODE_MAYA_XBM_PATH                = utilities.path_Builder(_CODE_MAYA,"icons")
_CODE_MAYA_BONUS_TOOLS_Contents    = utilities.path_Builder(_CODE_MAYA_SCRIPT_PATH, "MayaBonusTools", "Contents")
_CODE_MAYA_BONUS_TOOLS_ICONS       = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "icons")
_CODE_MAYA_BONUS_TOOLS_MEL         = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "scripts")
_CODE_MAYA_BONUS_TOOLS_MEL_2014    = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "scripts-2014")
_CODE_MAYA_BONUS_TOOLS_MEL_2015    = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "scripts-2015")
_CODE_MAYA_BONUS_TOOLS_PYTHON      = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "python")
_CODE_MAYA_BONUS_TOOLS_PYTHON_2014 = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "python-2014")
_CODE_MAYA_BONUS_TOOLS_PYTHON_2015 = utilities.path_Builder(_CODE_MAYA_BONUS_TOOLS_Contents, "python-2015")

# Nuke Paths
_CODE_NUKE              = utilities.path_Builder(_CODE_SOFTWARE, "Nuke")
_CODE_NUKE_GIZMOS       = utilities.path_Builder(_CODE_SOFTWARE, "Nuke_Gizmos")
_CODE_NUKE_USER_TOOLS   = utilities.path_Builder(_CODE_AW_USER_TOOLS, "Nuke_User_Tools")
_CODE_NUKE_PLUGINS      = utilities.path_Builder(_CODE_NUKE, "Plugins")

# Shotgun Paths
_CODE_SHOTGUN_EVENTS              = utilities.path_Builder(_CODE_SHOTGUN, "Event_Triggers")
_CODE_SHOTGUN_ACTION_MENU_ITEMS   = utilities.path_Builder(_CODE_SHOTGUN, "Shotgun_ActionMenu_Items")

#----------------------------------------------------------------------
AW_BASE                = utilities.get_and_set_environ_key("AW_BASE", default=_CODE_BASE, force_default=True)
#----------------------------------------------------------------------
AW_GLOBAL_SYSTEMS      = utilities.get_and_set_environ_key("AW_GLOBAL_SYSTEMS", default=_CODE_GLOBAL_SYSTEMS, force_default=True)
#----------------------------------------------------------------------
AW_SOFTWARE_SYSTEMS    = utilities.get_and_set_environ_key("AW_SOFTWARE_SYSTEMS", default=_CODE_SOFTWARE, force_default=True)
#----------------------------------------------------------------------
AW_ENVIRONMENT_ACCESS  = utilities.get_and_set_environ_key("AW_ENVIRONMENT_ACCESS", default=_CODE_ENVIRONMENT_ACCESS, force_default=True)
#----------------------------------------------------------------------
AW_SITE_PACKAGES       = utilities.get_and_set_environ_key("AW_SITE_PACKAGES", default=_CODE_AW_SITE_PACKAGES, force_default=True)
#----------------------------------------------------------------------
AW_USER_TOOLS          = utilities.get_and_set_environ_key("AW_USER_TOOLS", default=_CODE_AW_USER_TOOLS, force_default=True)
#----------------------------------------------------------------------
##NUKE_USER_TOOLS_DIR    = utilities.get_and_set_environ_key("NUKE_USER_TOOLS_DIR", default=_CODE_NUKE_USER_TOOLS, force_default=True)
NUKE_USER_TOOLS_DIR    = utilities.get_and_set_environ_key("NUKE_USER_TOOLS_DIR", default=_CODE_NUKE_USER_TOOLS, force_default=True)
#----------------------------------------------------------------------
MAYA_USER_TOOLS_DIR    = utilities.get_and_set_environ_key("MAYA_USER_TOOLS_DIR", default=_CODE_MAYA_USER_TOOLS, force_default=True)
#----------------------------------------------------------------------
AW_COMMON_UTILITIES    = utilities.get_and_set_environ_key("AW_COMMON_UTILITIES", default=_CODE_COMMON_UTILITIES, force_default=True)


utilities.add_To_System_Path(AW_GLOBAL_SYSTEMS)