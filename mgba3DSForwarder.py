import glob, sys, subprocess, os, logging
from shutil import rmtree

logfile = "\\" + "Forwarder.log"
prereqs = ['path.txt','banner.bnr','icon.icn']
cia_folders = []
total_processed = 0
total_failed = []

# Delete old logfile when script is run.
if os.path.exists(sys.path[0]+logfile): os.remove(sys.path[0]+logfile)

# Set up the logging module, so that it prints to a log file (sys.path[0] is the directory this script is in) as well as to the console (sys.stdout). Now use logging.info() instead of print().
logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s]: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', handlers=[logging.FileHandler(sys.path[0] + logfile), logging.StreamHandler(sys.stdout)])
logging.info("Script Working Directory: "+sys.path[0])

# Check to see if script was run with arguments (e.g. file/folder dragged onto it). If not, ask the user for input.
try:
	inpath = sys.argv[1]
except:
	inpath = input("Please input FULL path to folder containing each of the forwarder subfolders: ")

if not os.path.exists(os.path.join(sys.path[0], 'mgba')):
	raise Exception("Please ensure the modified mgba source code is present in an 'mgba' folder in the same directory as this script.")

# Set up function to validate necessary files for generating forwarder CIA exist within each folder
def validatePrereqs(folder):
	folderfiles = []

	# Append a wildcard to the end of the path to let the glob iterator know it should search for all files in the directory/subdirs.
	folder += '\\**'

	for infile in glob.iglob(folder, recursive=True):
		# os.path.split supplies a tuple, first value is the directory the file is in, second is the filename.
		# We first check infile is a file, not a directory, otherwise the split function gets confused.
		if not os.path.isdir(infile):
			filepath, filename = os.path.split(infile)
			folderfiles.append(filename)

	if prereqs.sort() == folderfiles.sort():
		return True
	else:
		return False

def generateScript(parsed_path):
	# Literally I cannot fathom why subprocess.run() refuses to just run the goddamn docker run command by itself but it fails inexplicably unless its run from an external shell.
	# The scriptfile below cannot be named docker.bat, or when the batch file tries to run "docker run" instead of calling "(PATH)/docker.exe run" it'll be calling "./docker.bat run" and running itself over and over again indefinitely. Hence dockerbuilder.bat. 
	script = f"docker run --rm -it -v {parsed_path} mgba/3ds"
	scriptfile = os.path.join(sys.path[0],'dockerbuilder.bat')
	logging.info(f"Generating script: {script}\nAt: {scriptfile}.")
	with open(scriptfile,'w+') as infile: infile.write(script)
	with open(scriptfile,'r') as infile:
		logging.info('Script written: %s' % infile.read())

# If the supplied path is a directory, then let the script know it will need to parse sub/dirs rather than a single file.
if os.path.isdir(inpath):
	# os.walk returns a 3-tuple, but we only need the 'files' value that it returns. Using '_' as a variable name for the other parts of the tuple throws them away.
	total_folders =  sum(len(folders) for _,folders,_ in os.walk(inpath))

	# Initial glob just gets the subdirectory for each cia to be generated
	for item in glob.iglob(inpath+"\\**", recursive=False):
		if os.path.isdir(item):
			cia_folders.append(item)

	logging.info("Cia Folder Path: "+inpath)
	logging.info("Detected Cia Folders: "+str(cia_folders))

	# Now walk through each of the subdirectories; each one should represent a .cia forwarder to be generated.
	for folder in cia_folders:
		logging.info("Now working on folder: "+folder+". Attempting to validate contents.")
		if validatePrereqs(os.path.join(inpath,folder)):
			logging.info("Contents valid.")
			# Remove old build files
			try:
				logging.info("Attempting to remove old build files...")
				rmtree(os.path.join(sys.path[0],'mgba','build-3ds','install'))
			except FileNotFoundError as BuildClearError:
				logging.info('Attempted to remove old buildfiles, FileNotFound error raised... No old build files exist. Moving on.')
			for item in prereqs:
				# For each of the files in each cia folder, remove the old file living in 3ds_custom_data folder then move the new file over to there
				logging.info("Attempting to remove old %s from 3ds_custom_data folder" % item)
				try:
					os.remove(os.path.join(sys.path[0], 'mgba', 'res', '3ds_custom_data', item))
				except:
					pass
				logging.info("Attempting to move new %s to 3ds_custom_data folder" % item)
				try:
					os.rename((os.path.join(folder, item)), os.path.join(sys.path[0], 'mgba', 'res', '3ds_custom_data', item))
				except FileNotFoundError:
					logging.exception('')
					raise
			logging.info("All items moved. Attempting to validate contents of 3ds_custom_data.")
			if validatePrereqs(os.path.join(sys.path[0], 'mgba', 'res', '3ds_custom_data')):
				# Correct files now exist in mgba, ready to build!
				logging.info("3ds_custom_data contents valid, will generate docker script.")
				total_processed += 1
				try:
					logging.info("Processing %s of %s, foldername: %s. " % (str(total_processed), str(total_folders), folder))
					parsed_path = '"//' + sys.path[0].replace('D:','d').replace("\\","/") + '/mgba' + '://home/mgba/src"'
					logging.info('Docker Volume Mount: %s' % parsed_path)
					generateScript(parsed_path)
					logging.info('Running docker batchfile now; if the build successfully starts this can take a while.')
					#  Redirecting the batch's stdout/err to PIPE ensures the build process is piped to the Python console, Check ensures this script throws an exception if the bat file fails.
					result = subprocess.run(["dockerbuilder.bat"], stdout=logging.info(subprocess.PIPE), stderr=logging.info(subprocess.PIPE), check=True)
					logging.info("Docker run completed... Removing batch file.")
					os.remove(os.path.join(sys.path[0],'dockerbuilder.bat'))
					try:
						# Move completed .cia out of the build folder and to the original cias directory subfolder
						logging.info("Now attempting to move built cia, if it exists.")
						os.rename(os.path.join(sys.path[0],'mgba','build-3ds','install','usr','local','cia','mgba.cia'),os.path.join(inpath, folder, folder + '.cia'))
					except FileNotFoundError:
						total_failed.append({'number_processed': str(total_processed), 'foldername': folder, 'returncode': '', 'stdout': 'Cia File Not Found', 'stderr': 'Cia File Not Found'})
						logging.exception('')
				except subprocess.CalledProcessError as DockerError:
					# If docker command fails, catches this as an error that Python can parse. Errors outputted in that bat file are found in stdout, stderr is often empty.
					total_failed.append({'number_processed': str(total_processed), 'foldername': folder, 'returncode': str(DockerError.returncode), 'stdout': str(DockerError.stdout), 'stderr': str(DockerError.stderr)})
			else:
				logging.info("Necessary files do not exist in 3ds_custom_data, cannot commence build.")
				raise Exception("Necessary files do not exist in 3ds_custom_data, cannot commence build.")
		else:
			logging.info("Necessary files do not exist in %s, cannot continue." % folder)
			raise Exception("Necessary files do not exist in %s, cannot continue." % folder)

logging.info("%s of %s files failed.\n\n" % (str(len(total_failed)), str(total_processed)))
for failure in total_failed: logging.info("\nFile: " + failure['foldername'] + "\n" + "Log:\n" + failure['stdout'] + "\n" + failure['stderr'] + "\n" + failure['returncode'] + "\n\n")