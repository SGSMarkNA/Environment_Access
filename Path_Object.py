""" path.py - An object representing a path to a file or directory.

Example:

from path import path
d = path('/home/guido/bin')
for f in d.files('*.py'):
    f.chmod(0755)

This module requires Python 2.2 or later.


URL:     http://www.jorendorff.com/articles/python/path
Author:  Jason Orendorff <jason.orendorff\x40gmail\x2ecom> (and others - see the url!)
Date:    7 Mar 2004
"""


# TODO
#   - Tree-walking functions don't avoid symlink loops.  Matt Harrison sent me a patch for this.
#   - Tree-walking functions can't ignore errors.  Matt Harrison asked for this.
#
#   - Two people asked for path.chdir().  This just seems wrong to me,
#     I dunno.  chdir() is moderately evil anyway.
#
#   - Bug in write_text().  It doesn't support Universal newline mode.
#   - Better error message in listdir() when self isn't a
#     directory. (On Windows, the error message really sucks.)
#   - Make sure everything has a good docstring.
#   - Add methods for regex find and replace.
#   - guess_content_type() method?
#   - Perhaps support arguments to touch().
#   - Could add split() and join() methods that generate warnings.

from __future__ import generators
import sys, warnings, os, fnmatch, glob, shutil, codecs, re, datetime

try:
	import grp
except ImportError:
	grp = None

__version__ = '2.1'
__all__ = ['path']

# Platform-specific support for path.owner
if os.name == 'nt':
	try:
		import win32security
	except ImportError:
		win32security = None
else:
	try:
		import pwd
	except ImportError:
		pwd = None

# Pre-2.3 support.  Are unicode filenames supported?
_base = str
_getcwd = os.getcwd
try:
	if os.path.supports_unicode_filenames:
		_base = unicode
		_getcwd = os.getcwdu
except AttributeError:
	pass

# Pre-2.3 workaround for booleans
try:
	True, False
except NameError:
	True, False = 1, 0

# Pre-2.3 workaround for basestring.
try:
	basestring
except NameError:
	basestring = (str, unicode)

# Universal newline support
_textmode = 'r'
if hasattr(file, 'newlines'):
	_textmode = 'U'


class PathWalkWarning(Warning):
	pass

def _handleException(exc, mode, warningObject):
	if mode == 'ignore':
		return
	elif mode == 'warn':
		warnings.warn(warningObject.__class__(warningObject.message % dict(exc=exc)))
	else:
		raise exc

class date_time_object(object):
	def __init__(self, full_path):
		self.path = Path(str(full_path))

	@property
	def ctime(self):
		return datetime.datetime.fromtimestamp(self.path.ctime)
	@property
	def mtime(self):
		return datetime.datetime.fromtimestamp(self.path.mtime)
	@property
	def atime(self):
		return datetime.datetime.fromtimestamp(self.path.atime)

	@property
	def date_created(self):
		return self.ctime.strftime("%A, %d. %B %Y %I:%M%p")
	@property
	def date_last_mod(self):
		return self.mtime.strftime("%A, %d. %B %Y %I:%M%p")
	@property
	def date_last_accessed(self):
		return self.atime.strftime("%A, %d. %B %Y %I:%M%p")


class path(_base):
	""" Represents a filesystem path.
	For documentation on individual methods, consult their
	counterparts in os.path.
	"""
	# --- Special Python methods.
	def __repr__(self):
		return 'path(%s)' % _base.__repr__(self)

	# Adding a path and a string yields a path.
	def __add__(self, more):
		try:
			resultStr = _base.__add__(self, more)
		except TypeError:  #Python bug
			resultStr = NotImplemented
		if resultStr is NotImplemented:
			return resultStr
		return self.__class__(resultStr)

	def __radd__(self, other):
		if isinstance(other, basestring):
			return self.__class__(other.__add__(self))
		else:
			return NotImplemented

	# The / operator joins paths.
	def __div__(self, rel):
		""" fp.__div__(rel) == fp / rel == fp.joinpath(rel)

		Join two path components, adding a separator character if
		needed.
		"""
		return self.__class__(os.path.join(self, rel))

	# Make the / operator work even when true division is enabled.
	__truediv__ = __div__

	@classmethod
	def getcwd(cls):
		""" Return the current working directory as a path object. """
		res = cls(_getcwd())
		isinstance(res,path)
		return res


	# --- Operations on path strings.

	isabs = os.path.isabs
	def abspath(self):
		res = self.__class__(os.path.abspath(self))
		isinstance(res,path)
		return res
	def normcase(self):
		res = self.__class__(os.path.normcase(self))
		isinstance(res,path)
		return res
	def normpath(self):
		res = self.__class__(os.path.normpath(self))
		isinstance(res,path)
		return res
	def realpath(self):
		res = self.__class__(os.path.realpath(self))
		isinstance(res,path)
		return res
	def expanduser(self):
		res = self.__class__(os.path.expanduser(self))
		isinstance(res,path)
		return res
	def expandvars(self):
		res = self.__class__(os.path.expandvars(self))
		isinstance(res,path)
		return res
	def dirname(self):
		res = self.__class__(os.path.dirname(self))
		isinstance(res,path)
		return res
	
	basename = os.path.basename

	def expand(self):
		""" Clean up a filename by calling expandvars(),
		expanduser(), and normpath() on it.

		This is commonly everything needed to clean up a filename
		read from a configuration file, for example.
		"""
		return self.expandvars().expanduser().normpath()

	@property
	def drive(self):
		"""
		The drive specifier, for example 'C:'.
		This is always empty on systems that don't use drive specifiers.
		"""
		drv, r = os.path.splitdrive(self)
		res = self.__class__(drv)
		isinstance(res,path)
		return res

	@property
	def parent(self):
		"""
		This path's parent directory, as a new path object.

		For example, path('/usr/local/lib/libpython.so').parent == path('/usr/local/lib')
		"""
		return self.dirname()
	@property
	def name(self):
		"""
		The name of this file or directory without the full path.

		For example, path('/usr/local/lib/libpython.so').name == 'libpython.so'
		"""
		return self.basename()
	@property
	def namebase(self):
		"""
		The same as path.name, but with one file extension stripped off.

		For example, path('/home/guido/python.tar.gz').name     == 'python.tar.gz',
		but          path('/home/guido/python.tar.gz').namebase == 'python.tar'
		"""
		base, ext = os.path.splitext(self.name)
		return base


	@property
	def ext(self):
		"""
		The file extension, for example '.py'.
		"""
		f, extn = os.path.splitext(_base(self))
		return extn

	def splitpath(self):
		""" p.splitpath() -> Return (p.parent, p.name). """
		parent, child = os.path.split(self)
		return self.__class__(parent), child

	def splitdrive(self):
		""" p.splitdrive() -> Return (p.drive, <the rest of p>).

		Split the drive specifier from this path.  If there is
		no drive specifier, p.drive is empty, so the return value
		is simply (path(''), p).  This is always the case on Unix.
		"""
		drive, rel = os.path.splitdrive(self)
		return self.__class__(drive), rel

	def splitext(self):
		""" p.splitext() -> Return (p.stripext(), p.ext).

		Split the filename extension from this path and return
		the two parts.  Either part may be empty.

		The extension is everything from '.' to the end of the
		last path segment.  This has the property that if
		(a, b) == p.splitext(), then a + b == p.
		"""
		filename, ext = os.path.splitext(self)
		return self.__class__(filename), ext

	def stripext(self):
		""" p.stripext() -> Remove one file extension from the path.

		For example, path('/home/guido/python.tar.gz').stripext()
		returns path('/home/guido/python.tar').
		"""
		res = self.splitext()[0]
		isinstance(res,path)
		return res
	
	if hasattr(os.path, 'splitunc'):
		def splitunc(self):
			unc, rest = os.path.splitunc(self)
			return self.__class__(unc), rest

		def _get_uncshare(self):
			unc, r = os.path.splitunc(self)
			return self.__class__(unc)

		uncshare = property(
			_get_uncshare, None, None,
			""" The UNC mount point for this path.
            This is empty for paths on local drives. """)

	def joinpath(self, *args):
		""" Join two or more path components, adding a separator
		character (os.sep) if needed.  Returns a new path
		object.
		"""
		res = self.__class__(os.path.join(self, *args))
		isinstance(res,path)
		return res

	def splitall(self):
		r""" Return a list of the path components in this path.

		The first item in the list will be a path.  Its value will be
		either os.curdir, os.pardir, empty, or the root directory of
		this path (for example, '/' or 'C:\\').  The other items in
		the list will be strings.

		path.path.joinpath(*result) will yield the original path.
		"""
		parts = []
		loc = self
		while loc != os.curdir and loc != os.pardir:
			prev = loc
			loc, child = prev.splitpath()
			if loc == prev:
				break
			parts.append(child)
		parts.append(loc)
		parts.reverse()
		return parts

	def relpath(self):
		""" Return this path as a relative path,
		based from the current working directory.
		"""
		cwd = self.__class__(os.getcwd())
		return cwd.relpathto(self)

	def relpathto(self, dest):
		""" Return a relative path from self to dest.

		If there is no relative path from self to dest, for example if
		they reside on different drives in Windows, then this returns
		dest.abspath().
		"""
		origin = self.abspath()
		dest = self.__class__(dest).abspath()

		orig_list = origin.normcase().splitall()
		# Don't normcase dest!  We want to preserve the case.
		dest_list = dest.splitall()

		if orig_list[0] != os.path.normcase(dest_list[0]):
			# Can't get here from there.
			return dest

		# Find the location where the two paths start to differ.
		i = 0
		for start_seg, dest_seg in zip(orig_list, dest_list):
			if start_seg != os.path.normcase(dest_seg):
				break
			i += 1

		# Now i is the point where the two paths diverge.
		# Need a certain number of "os.pardir"s to work up
		# from the origin to the point of divergence.
		segments = [os.pardir] * (len(orig_list) - i)
		# Need to add the diverging part of dest_list.
		segments += dest_list[i:]
		if len(segments) == 0:
			# If they happen to be identical, use os.curdir.
			relpath = os.curdir
		else:
			relpath = os.path.join(*segments)
		res = self.__class__(relpath)
		isinstance(res,path)
		return res
	# --- Listing, searching, walking, and matching

	def listdir(self, pattern=None):
		""" D.listdir() -> List of items in this directory.

		Use D.files() or D.dirs() instead if you want a listing
		of just files or just subdirectories.

		The elements of the list are path objects.

		With the optional 'pattern' argument, this only lists
		items whose names match the given pattern.
		"""
		names = os.listdir(self)
		if pattern is not None:
			names = fnmatch.filter(names, pattern)
		return [self / child for child in names]

	def dirs(self, pattern=None, realpath=False):
		""" D.dirs() -> List of this directory's subdirectories.

		The elements of the list are path objects.
		This does not walk recursively into subdirectories
		(but see path.walkdirs).

		With the optional 'pattern' argument, this only lists
		directories whose names match the given pattern.  For
		example, d.dirs('build-*').
		"""
		if realpath:
			return [p.realpath() for p in self.listdir(pattern) if p.isdir()]
		else:
			return [p for p in self.listdir(pattern) if p.isdir()]

	def files(self, pattern=None):
		""" D.files() -> List of the files in this directory.

		The elements of the list are path objects.
		This does not walk into subdirectories (see path.walkfiles).

		With the optional 'pattern' argument, this only lists files
		whose names match the given pattern.  For example,
		d.files('*.pyc').
		"""

		return [p for p in self.listdir(pattern) if p.isfile()]

	def walk(self, pattern=None, errors='strict', regex=None ):
		""" D.walk() -> iterator over files and subdirs, recursively.

		The iterator yields path objects naming each child item of
		this directory and its descendants.  This requires that
		D.isdir().

		This performs a depth-first traversal of the directory tree.
		Each directory is returned just before all its children.

		The errors= keyword argument controls behavior when an
		error occurs.  The default is 'strict', which causes an
		exception.  The other allowed values are 'warn', which
		reports the error via warnings.warn(), and 'ignore'.
		"""
		if errors not in ('strict', 'warn', 'ignore'):
			raise ValueError("invalid errors parameter")

		try:
			childList = self.listdir()
		except Exception, exc:
			_handleException(exc,errors,
						     PathWalkWarning("Unable to list directory '%s': %%(exc)s" % self ))
		else:
			for child in childList:
				if ( pattern is None or child.fnmatch(pattern) ) and ( regex is None or re.match( regex, child.name ) ):
					yield child
					try:
						isdir = child.isdir()
					except Exception, exc:
						_handleException(exc,errors,PathWalkWarning("Unable to access '%s': %%(exc)s" % self))

					if isdir:
						for item in child.walk(pattern=pattern, errors=errors, regex=regex):
							yield item

	def walkdirs(self, pattern=None, errors='strict', realpath=False, regex=None):
		""" D.walkdirs() -> iterator over subdirs, recursively.

		With the optional 'pattern' argument, this yields only
		directories whose names match the given pattern.  For
		example, mydir.walkdirs('*test') yields only directories
		with names ending in 'test'.

		The errors= keyword argument controls behavior when an
		error occurs.  The default is 'strict', which causes an
		exception.  The other allowed values are 'warn', which
		reports the error via warnings.warn(), and 'ignore'.
		"""
		if errors not in ('strict', 'warn', 'ignore'):
			raise ValueError("invalid errors parameter")

		try:
			dirs = self.dirs(realpath=realpath)
		except Exception, exc:
			_handleException(exc,errors,PathWalkWarning("Unable to list directory '%s': %%(exc)s" % self))
		else:
			parent_realpath = None
			for child in dirs:
				if ( pattern is None or child.fnmatch(pattern) ) and ( regex is None or re.match( regex, child.name ) ):
					if child.islink():
						if parent_realpath is None:
							parent_realpath = self.realpath()
						if realpath:
							child_realpath = child
						else:
							child_realpath = child.realpath()
						# check for infinite recursion
						if child_realpath == parent_realpath or parent_realpath.startswith( child_realpath + os.path.sep ):
							#print "skipping %s to prevent infinite recursion" % child
							continue
						else:
							yield child
					else:
						yield child

					for subsubdir in child.walkdirs(pattern, errors=errors, realpath=realpath, regex=regex):
						yield subsubdir

	def walkfiles(self, pattern=None, errors='strict', regex=None):
		""" D.walkfiles() -> iterator over files in D, recursively.

		The optional argument, pattern, limits the results to files
		with names that match the pattern.  For example,
		mydir.walkfiles('*.tmp') yields only files with the .tmp
		extension.
		"""
		if errors not in ('strict', 'warn', 'ignore'):
			raise ValueError("invalid errors parameter")

		try:
			childList = self.listdir()
		except Exception, exc:
			_handleException(exc,errors,PathWalkWarning("Unable to list directory '%s': %%(exc)s" % self))
		else:
			for child in childList:
				try:
					isfile = child.isfile()
					isdir = not isfile and child.isdir()
				except Exception, exc:
					_handleException(exc,errors,PathWalkWarning("Unable to access '%s': %%(exc)s" % self) )
				else:

					if isfile:
						if ( pattern is None or child.fnmatch(pattern) ) and ( regex is None or re.match( regex, child.name ) ):
							yield child
					elif isdir:
						for f in child.walkfiles(pattern=pattern, errors=errors, regex=regex):
							yield f

	def fnmatch(self, pattern):
		""" Return True if self.name matches the given pattern.

		pattern - A filename pattern with wildcards,
		    for example '*.py'.
		"""
		return fnmatch.fnmatch(self.name, pattern)

	def glob(self, pattern):
		""" Return a list of path objects that match the pattern.

		pattern - a path relative to this directory, with wildcards.

		For example, path('/users').glob('*/bin/*') returns a list
		of all the files users have in their bin directories.
		"""
		return [self.__class__(s) for s in glob.glob(_base(self / pattern))]


	# --- Reading or writing an entire file at once.

	def open(self, mode='r'):
		""" Open this file.  Return a file object. """
		return file(self, mode)

	def bytes(self):
		""" Open this file, read all bytes, return them as a string. """
		f = self.open('rb')
		try:
			return f.read()
		finally:
			f.close()

	def write_bytes(self, bytes, append=False):
		""" Open this file and write the given bytes to it.

		Default behavior is to overwrite any existing file.
		Call p.write_bytes(bytes, append=True) to append instead.
		"""
		if append:
			mode = 'ab'
		else:
			mode = 'wb'
		f = self.open(mode)
		try:
			f.write(bytes)
		finally:
			f.close()

	def text(self, encoding=None, errors='strict'):
		r""" Open this file, read it in, return the content as a string.

		This uses 'U' mode in Python 2.3 and later, so '\r\n' and '\r'
		are automatically translated to '\n'.

		Optional arguments:

		encoding - The Unicode encoding (or character set) of
		    the file.  If present, the content of the file is
		    decoded and returned as a unicode object; otherwise
		    it is returned as an 8-bit str.
		errors - How to handle Unicode errors; see help(str.decode)
		    for the options.  Default is 'strict'.
		"""
		if encoding is None:
			# 8-bit
			f = self.open(_textmode)
			try:
				return f.read()
			finally:
				f.close()
		else:
			# Unicode
			f = codecs.open(self, 'r', encoding, errors)
			# (Note - Can't use 'U' mode here, since codecs.open
			# doesn't support 'U' mode, even in Python 2.3.)
			try:
				t = f.read()
			finally:
				f.close()
			return (t.replace(u'\r\n', u'\n')
					.replace(u'\r\x85', u'\n')
					.replace(u'\r', u'\n')
					.replace(u'\x85', u'\n')
					.replace(u'\u2028', u'\n'))

	def write_text(self, text, encoding=None, errors='strict', linesep=os.linesep, append=False):
		r""" Write the given text to this file.

		The default behavior is to overwrite any existing file;
		to append instead, use the 'append=True' keyword argument.

		There are two differences between path.write_text() and
		path.write_bytes(): newline handling and Unicode handling.
		See below.

		Parameters:

		  - text - str/unicode - The text to be written.

		  - encoding - str - The Unicode encoding that will be used.
		    This is ignored if 'text' isn't a Unicode string.

		  - errors - str - How to handle Unicode encoding errors.
		    Default is 'strict'.  See help(unicode.encode) for the
		    options.  This is ignored if 'text' isn't a Unicode
		    string.

		  - linesep - keyword argument - str/unicode - The sequence of
		    characters to be used to mark end-of-line.  The default is
		    os.linesep.  You can also specify None; this means to
		    leave all newlines as they are in 'text'.

		  - append - keyword argument - bool - Specifies what to do if
		    the file already exists (True: append to the end of it;
		    False: overwrite it.)  The default is False.


		--- Newline handling.

		write_text() converts all standard end-of-line sequences
		('\n', '\r', and '\r\n') to your platform's default end-of-line
		sequence (see os.linesep; on Windows, for example, the
		end-of-line marker is '\r\n').

		If you don't like your platform's default, you can override it
		using the 'linesep=' keyword argument.  If you specifically want
		write_text() to preserve the newlines as-is, use 'linesep=None'.

		This applies to Unicode text the same as to 8-bit text, except
		there are three additional standard Unicode end-of-line sequences:
		u'\x85', u'\r\x85', and u'\u2028'.

		(This is slightly different from when you open a file for
		writing with fopen(filename, "w") in C or file(filename, 'w')
		in Python.)


		--- Unicode

		If 'text' isn't Unicode, then apart from newline handling, the
		bytes are written verbatim to the file.  The 'encoding' and
		'errors' arguments are not used and must be omitted.

		If 'text' is Unicode, it is first converted to bytes using the
		specified 'encoding' (or the default encoding if 'encoding'
		isn't specified).  The 'errors' argument applies only to this
		conversion.

		"""
		if isinstance(text, unicode):
			if linesep is not None:
				# Convert all standard end-of-line sequences to
				# ordinary newline characters.
				text = (text.replace(u'\r\n', u'\n')
						.replace(u'\r\x85', u'\n')
						.replace(u'\r', u'\n')
						.replace(u'\x85', u'\n')
						.replace(u'\u2028', u'\n'))
				text = text.replace(u'\n', linesep)
			if encoding is None:
				encoding = sys.getdefaultencoding()
			bytes = text.encode(encoding, errors)
		else:
			# It is an error to specify an encoding if 'text' is
			# an 8-bit string.
			assert encoding is None

			if linesep is not None:
				text = (text.replace('\r\n', '\n')
						.replace('\r', '\n'))
				bytes = text.replace('\n', linesep)

		self.write_bytes(bytes, append)

	def lines(self, encoding=None, errors='strict', retain=True):
		r""" Open this file, read all lines, return them in a list.

		Optional arguments:
		    encoding - The Unicode encoding (or character set) of
		        the file.  The default is None, meaning the content
		        of the file is read as 8-bit characters and returned
		        as a list of (non-Unicode) str objects.
		    errors - How to handle Unicode errors; see help(str.decode)
		        for the options.  Default is 'strict'
		    retain - If true, retain newline characters; but all newline
		        character combinations ('\r', '\n', '\r\n') are
		        translated to '\n'.  If false, newline characters are
		        stripped off.  Default is True.

		This uses 'U' mode in Python 2.3 and later.
		"""
		if encoding is None and retain:
			f = self.open(_textmode)
			try:
				return f.readlines()
			finally:
				f.close()
		else:
			return self.text(encoding, errors).splitlines(retain)

	def write_lines(self, lines, encoding=None, errors='strict',
		            linesep=os.linesep, append=False):
		r""" Write the given lines of text to this file.

		By default this overwrites any existing file at this path.

		This puts a platform-specific newline sequence on every line.
		See 'linesep' below.

		lines - A list of strings.

		encoding - A Unicode encoding to use.  This applies only if
		    'lines' contains any Unicode strings.

		errors - How to handle errors in Unicode encoding.  This
		    also applies only to Unicode strings.

		linesep - The desired line-ending.  This line-ending is
		    applied to every line.  If a line already has any
		    standard line ending ('\r', '\n', '\r\n', u'\x85',
		    u'\r\x85', u'\u2028'), that will be stripped off and
		    this will be used instead.  The default is os.linesep,
		    which is platform-dependent ('\r\n' on Windows, '\n' on
		    Unix, etc.)  Specify None to write the lines as-is,
		    like file.writelines().

		Use the keyword argument append=True to append lines to the
		file.  The default is to overwrite the file.  Warning:
		When you use this with Unicode data, if the encoding of the
		existing data in the file is different from the encoding
		you specify with the encoding= parameter, the result is
		mixed-encoding data, which can really confuse someone trying
		to read the file later.
		"""
		if append:
			mode = 'ab'
		else:
			mode = 'wb'
		f = self.open(mode)
		try:
			for line in lines:
				isUnicode = isinstance(line, unicode)
				if linesep is not None:
					# Strip off any existing line-end and add the
					# specified linesep string.
					if isUnicode:
						if line[-2:] in (u'\r\n', u'\x0d\x85'):
							line = line[:-2]
						elif line[-1:] in (u'\r', u'\n',
										   u'\x85', u'\u2028'):
							line = line[:-1]
					else:
						if line[-2:] == '\r\n':
							line = line[:-2]
						elif line[-1:] in ('\r', '\n'):
							line = line[:-1]
					line += linesep
				if isUnicode:
					if encoding is None:
						encoding = sys.getdefaultencoding()
					line = line.encode(encoding, errors)
				f.write(line)
		finally:
			f.close()

	def read_md5(self):
		""" Calculate the md5 hash for this file.

		This reads through the entire file.
		"""

		f = self.open('rb')
		try:
			m = None
			try:
				# fix for python 2.5 - module md5 is deprecated and now part of new hashlib
				import hashlib
				m = hashlib.md5()
			except ImportError:
				import md5
				m = md5.new()
			while True:
				d = f.read(8192)
				if not d:
					break
				m.update(d)
		finally:
			f.close()
		return m.digest()

	# --- Methods for querying the filesystem.

	exists = os.path.exists
	isdir = os.path.isdir
	isfile = os.path.isfile
	islink = os.path.islink
	ismount = os.path.ismount
	
	@property
	def datetime_object(self):
		return date_time_object(self)

	if hasattr(os.path, 'samefile'):
		samefile = os.path.samefile

	def samepath(self, otherpath):
		"""Whether the other path represents the same path as this one.

		This will account for symbolic links, absolute/relative paths,
		case differences (if on a case-insensitive file system), and '..'
		usage (so paths such as A//B, A/./B and A/foo/../B will all compare equal).

		This will NOT account for hard links - use 'samefile' for this, if
		available on your os.

		Essentially just compares the self.canonicalpath() to other.canonicalpath()
		"""
		return self.canonicalpath() == self.__class__(otherpath).canonicalpath()

	def canonicalpath(self):
		"""Attempt to return a 'canonical' version of the path

		This will standardize for symbolic links, absolute/relative paths,
		case differences (if on a case-insensitive file system), and '..'
		usage (so paths such as A//B, A/./B and A/foo/../B will all compare equal).

		The intention is that string comparison of canonical paths will yield
		a reasonable guess as to whether two paths represent the same file.
		"""
		return self.__class__(self.abspath().realpath().normpath().normcase())

	def truepath(self):
		"""The absolute, real, normalized path.

		Shortcut for .abspath().realpath().normpath()

		Unlike canonicalpath, on case-sensitive filesystems, two different paths
		may refer the same file, and so should only be used in cases where a
		"normal" path from root is desired, but we wish to preserve case; in
		situations where comparison is desired, canonicalpath (or samepath)
		should be used.
		"""
		return self.__class__(self.abspath().realpath().normpath())

	getatime = os.path.getatime
	atime = property(getatime, None, None,""" Last access time of the file. """)
	getmtime = os.path.getmtime
	mtime = property(getmtime, None, None,""" Last-modified time of the file. """)

	if hasattr(os.path, 'getctime'):
		getctime = os.path.getctime
		ctime = property(getctime, None, None,""" Creation time of the file. """)

	getsize = os.path.getsize
	size = property(getsize, None, None,""" Size of the file, in bytes. """)

	if hasattr(os, 'access'):
		def access(self, mode):
			""" Return true if current user has access to this path.

			mode - One of the constants os.F_OK, os.R_OK, os.W_OK, os.X_OK
			"""
			return os.access(self, mode)

	def stat(self):
		""" Perform a stat() system call on this path. """
		return os.stat(self)

	def lstat(self):
		""" Like path.stat(), but do not follow symbolic links. """
		return os.lstat(self)

	def get_owner(self):
		r""" Return the name of the owner of this file or directory.

		This follows symbolic links.

		On Windows, this returns a name of the form ur'DOMAIN\User Name'.
		On Windows, a group can own a file or directory.
		"""
		if os.name == 'nt':
			if win32security is None:
				raise Exception("path.owner requires win32all to be installed")
			desc = win32security.GetFileSecurity(
				self, win32security.OWNER_SECURITY_INFORMATION)
			sid = desc.GetSecurityDescriptorOwner()
			account, domain, typecode = win32security.LookupAccountSid(None, sid)
			return domain + u'\\' + account
		else:
			if pwd is None:
				raise NotImplementedError("path.owner is not implemented on this platform.")
			st = self.stat()
			return pwd.getpwuid(st.st_uid).pw_name

	owner = property(get_owner, None, None,""" Name of the owner of this file or directory. """)

	if grp:
		def get_groupname(self):
			"""get the group name for this file"""
			return grp.getgrgid(self.stat().st_gid).gr_name
		groupname = property( get_groupname )

		def chgrp(self, group):
			if isinstance(group, basestring):
				group = grp.getgrnam(group).gr_gid
			os.chown( self, -1, group )

	if hasattr(os, 'statvfs'):
		def statvfs(self):
			""" Perform a statvfs() system call on this path. """
			return os.statvfs(self)

	if hasattr(os, 'pathconf'):
		def pathconf(self, name):
			return os.pathconf(self, name)


	# --- Modifying operations on files and directories

	def utime(self, times):
		""" Set the access and modified times of this file. """
		os.utime(self, times)

	def chmod(self, mode):
		os.chmod(self, mode)

	if hasattr(os, 'chown'):
		def chown(self, uid, gid):
			os.chown(self, uid, gid)

	def rename(self, new):
		os.rename(self, new)

	def renames(self, new):
		os.renames(self, new)


	# --- Create/delete operations on directories

	def mkdir(self, mode=0777):
		os.mkdir(self, mode)

	def makedirs(self, mode=0777):
		os.makedirs(self, mode)

	def rmdir(self):
		os.rmdir(self)

	def removedirs(self):
		os.removedirs(self)

	file_name = property(basename,rename)
	
	# --- Modifying operations on files

	def touch(self):
		""" Set the access/modified times of this file to the current time.
		Create the file if it does not exist.
		"""
		fd = os.open(self, os.O_WRONLY | os.O_CREAT, 0666)
		os.close(fd)
		os.utime(self, None)

	def remove(self):
		os.remove(self)

	def unlink(self):
		os.unlink(self)


	# --- Links

	if hasattr(os, 'link'):
		def link(self, newpath):
			""" Create a hard link at 'newpath', pointing to this file. """
			os.link(self, newpath)

	if hasattr(os, 'symlink'):
		def symlink(self, newlink):
			""" Create a symbolic link at 'newlink', pointing here. """
			os.symlink(self, newlink)

	if hasattr(os, 'readlink'):
		def readlink(self):
			""" Return the path to which this symbolic link points.

			The result may be an absolute or a relative path.
			"""
			return self.__class__(os.readlink(self))

		def readlinkabs(self):
			""" Return the path to which this symbolic link points.

			The result is always an absolute path.
			"""
			p = self.readlink()
			if p.isabs():
				return p
			else:
				return (self.parent / p).abspath()


	# --- High-level functions from shutil

	copyfile = shutil.copyfile
	copymode = shutil.copymode
	copystat = shutil.copystat
	copy = shutil.copy
	copy2 = shutil.copy2
	copytree = shutil.copytree
	if hasattr(shutil, 'move'):
		move = shutil.move
	rmtree = shutil.rmtree


	# --- Special stuff from os

	if hasattr(os, 'chroot'):
		def chroot(self):
			os.chroot(self)

	if hasattr(os, 'startfile'):
		def startfile(self):
			os.startfile(self)


# migrating to PEP8 compliance
Path = path
