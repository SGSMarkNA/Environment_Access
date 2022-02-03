import os
from Path_Object import Path
#----------------------------------------------------------------------
def make_Path_Object(path):
	""""""
	if not isinstance(path, Path):
		path = Path(path)
	return path
#----------------------------------------------------------------------
def path_fixer(path):
	"""OS File Path Standerizer"""
	# Check If The Input Is A Correct
	if isinstance(path, (str, unicode)):
		# Expand shell variables of form $var and ${var}.
		# Unknown variables are left unchanged.
		path = os.path.expandvars(path)
		# Check If This Is Being Run On A Windows Based OS
		if os.name == "nt":
			return path.replace("/", "\\")
		else:
			return path.replace("\\", "/")
	else:
		raise ValueError("The Input Expected Of Type String And A %r Was Found" % type(path))
#----------------------------------------------------------------------
def path_Builder(*args, **kwargs):
	""""""
	path =  os.path.join(*args)
	path = path_fixer(path)
	if kwargs.get("as_Path_Object", False):
		path = make_Path_Object(path)
	return path
#----------------------------------------------------------------------
def multi_Path_Builder(paths, **kwargs):
	""""""
	res = []
	for path in paths:
		path = path_fixer(path)
		if kwargs.get("as_Path_Object", False):
			path = make_Path_Object(path)
		res.append(path)
	res = os.path.pathsep.join(res)
	return res
#----------------------------------------------------------------------
def add_To_System_Path(path):
	"""Formats The Path And Adds The Input Path To The System Paths
	   Only If It Is A Valid Path And It Does Not Allready Exist"""
	# Check If The Input Is A Correct
	if isinstance(path, (str, unicode)):
		# Format The Path To Match The Operating System
		path = path_fixer(path)
		# Check If The Path Exists On The OS
		if os.path.exists(path):
			# Check If The Path Is Not Allready In The List Of System Paths
			if not path in os.sys.path:
				os.sys.path.append(path)
		else:
			# Raise An Error Telling The That The Input Path Does Not Exist
			raise ValueError("Can Not Add The Path %r Because It Does Not Exist" % path)
	else:
		# Raise An Error Telling The Wrong Input Was Given
		raise ValueError("The Input Expected Of Type String And A %r Was Found" % type(path))
#----------------------------------------------------------------------
def get_and_set_environ_key(key, default=None, force_default=False):
	"""Sets The Input Environment Key To Eather The Found Value Or The Default Value If The Key Does Not Exist Or Force Default Is True And Returns The Set Value"""
	# Check If Force Is True
	if force_default:
		# If So Set The Value To The Default Input
		res = default
	else:
		# If Not Get The key Value With The Default Bing The Fallback
		res = os.environ.get(key, default)
	# Applay The value To the input key
	os.environ[key] = res
	# Return The Value That was Set To The Key
	return res
#----------------------------------------------------------------------
def get_and_set_system_path_environ_key(key, default_path=None, force_default=False):
	"""Sets The Input Environment Key To Eather The Found Value Or The Default Value If The Key Does Not Exist Or Force Default Is True And Returns The Set Value
	   If The Found Value Is Not A Valid Path And The Default Value Is Not Set Or Is Not A Valid Path Raises A Value Error
	"""
	# Set The Values That Determens Weather Or Not The Default Path Input And The Environment Key Input Is A Valid File Path
	default_path_exists    = False
	environment_path_exists = False

	# Check If The Default Input Path Value Has Been Set
	if default_path is not None:
		# If So Check If The Default Path Exists
		if os.path.exists(default_path):
			# If So Changed The Default Value Check
			default_path_exists = True

	# Get The Path Value Of The Input Environment Key
	environment_path = os.environ.get(key, None)

	# Check If The Input Environment Key Had A Value
	if not environment_path is None:
		# If So Check If The Environment Path Exists
		if os.path.exists(environment_path):
			# If So Changed The Environment Path Value Check
			environment_path_exists = True

	# Check If The Key Did Not Have A Value And If The Default Path Has Not Been Set
	if environment_path is None and default_path is None:
		# Raise An Error Telling The That The Input Key Does Not Exist
		raise ValueError("The Input Key %r Does Not Exist And A Default Path Was Not Given" % key)

	# Check If No Valid Path Was Found
	if not any([environment_path_exists, default_path_exists]):
		# Raise An Error Telling The That No Valid Path Was Found
		raise ValueError("No Valid Path Was Found For Key %r Or The Default %r " % (environment_path, default_path))

	if all([environment_path_exists, default_path_exists, force_default]) or (not environment_path_exists and default_path_exists):
		res = default_path
	else:
		res = environment_path

	# Apply The value To the input key
	os.environ[key] = res
	# Return The Value That was Set To The Key
	return res
#----------------------------------------------------------------------
def add_To_Multi_Path_Environment_Key(key, paths):
	"""Adds File Or Folder Paths To An Existing Multi Path Environment Variable
	   in the From Of 'path_A;path_B;path_C'
	   and If it does Not allready Contain it adds the input path to end 'path_A;path_B;path_C:input_path'
	   If No Key Exists Makes A New One With The Given Paths
	"""
	# Check If The Input Key Exists In The Environment
	if os.environ.has_key(key):
		# Get The Environment key Value And Split It Up
		current_Value = os.environ.get(key).split(";")
	else:
		# Make An Empty List As A Default Value
		current_Value = []

	# Check If The Input Was A Single Path
	if isinstance(paths, (str, unicode)):
		# If So Convert It Into A List With A Single Item
		paths = [paths]

	# Check To Make Sure We Are Working With A List Of Paths
	if not isinstance(paths, list):
		raise ValueError("The Input Expected A Type String Or List And A %r Was Found" % type(paths))

	# Scan Though Each Item In Input Paths
	for i, item in enumerate(paths):
		# Check To Make Sure The Item Is A String
		if not isinstance(item, (str, unicode)):
			raise ValueError("All Items From The Input Need To Of Type String And A %r Was Found At Index %i" % (type(item), i) )
		# Conform The Path To The Proper OS format
		item = path_fixer(item)
		# Check If The Item Is Not Allready Present
		if not item in current_Value:
			# Add It To The List Of Current Values
			current_Value.append(item)

	# Take The Current List Of Paths And Condence Them Back Into A Single String Seperated By ;
	current_Value = ";".join(current_Value)

	# Reapply To The Environment Key
	os.environ[key] = current_Value

