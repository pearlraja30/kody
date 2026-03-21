Django2exe is a project to help you distribute your django project as exe

Credits:

	-Chirag Jain (jain.chirag925@gmail.com)

	-WinPython

	-Cefpython3


Setting Up

	-Run setup.bat to install django and cefpython3

	-After successful installation you can delete setup.bat and setup_requirements.txt

	-The app folder is a sample django project which you can delete

	-Paste your Django project folder where app folder is placed(it is recommended to compile all .py files to .pyc and delete all .py files, this will protect your source code.If you don't django2exe will compile all .py to .pyc but won't delete your .py files)

	-In the config folder paste the icon you want on the application window

	-Edit the config.json to get it all running

		-project_dir_name -> Name of your django projec folder

		Rest all settings are self-explanatory

	-Install all your pip requirements and migrations using the terminal which can be launched by executing py-dist\scripts\cmd.bat

	-When all done, try launching the your application with launch.bat



Contents:
	setup.bat and setup_requirements.txt:
		
		-sets up django and cefpython3 using pip.DELETE THESE FILES IN PRODUCTION DISTRIBUTIONS

	launchapp.bat
		
		-script to launch the application with a console to see log errors.DELETE THIS FILE IN PRODUCTION DISTRIBUTIONS

	launchapp.exe
		
		-launchapp.bat converted to exe with invisible console.Rename this to your application name

	app/

		-Just a sample Django project for structure reference

	config/

		-contains icon for application window

		-config.json for settings for the application

	py-dist/

		-The py-dist folder has portable python with some extra packages like pip installed

		-There is also a run.py in py-dist folder which launches the web server and the windows application.It also
		takes care of killing processes on exit

			What run.py does

				-A application is made with pyqt
				-A cef component is placed into the application using cefpython3
				-A manage.pyc runserver process is spawned on port 5423 on localhost
				-cef webkit is made to navigate to 127.0.0.1:5432

				NOTE: IF YOU WANT TO NAVIGATE TO SOME OTHER URL OR WANT TO BIND TO SOME OTHER PORT FEEL FREE TO EDIT run.py

		scripts/

			-env.bat
				setups portable python environment

			-cmd.bat
				setups portable python environment and starts cmd in the environment

			-python
				portable python console