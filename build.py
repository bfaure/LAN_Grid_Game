import os
import sys
import shutil

print("Building binary...")

if sys.platform in ["apple","Apple","darwin","Darwin"]:
	print("Found OS: Mac")
	targ_folder = "bin/Mac"

if sys.platform in ["win32"]: 
	print("Found OS: Windows")
	targ_folder = "bin/Windows"

if not os.path.isdir(targ_folder):
	print("Creating "+targ_folder)
	os.mkdir(targ_folder)
else:
	print("Removing prior build")
	shutil.rmtree(targ_folder)
	os.mkdir(targ_folder)

command = "pyinstaller --clean --onefile main.py --distpath="+targ_folder
print("Calling: "+command)

try:
	os.system(command)
except:
	print("Could not call pyinstaller!")

print("\nPyinstaller finished successfully")

print("Cleaning...")
if os.path.isdir("build"):
	shutil.rmtree("build")
if os.path.isfile("main.spec"):
	os.remove("main.spec")

print("Copying resources...")
shutil.copytree("resources",targ_folder+"/resources")

print("\n")
print("The compiled binary can be found at "+targ_folder)
print("Done")



