import os
import shutil
import zipfile

def package_app():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, 'dist_package')
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # Folders and files to include
    to_include = [
        'app',
        'py-dist',
        'config',
        'Kodys Foot Clinik.exe',
        'launchapp.bat',
        'appicon.ico',
        'readme.txt'
    ]

    print("Copying files to distribution folder...")
    for item in to_include:
        src = os.path.join(root_dir, item)
        dst = os.path.join(dist_dir, item)
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '.git', '.DS_Store', 'Dockerfile', 'docker-compose.yml'
                ))
            else:
                shutil.copy2(src, dst)
        else:
            print("Warning: {} not found".format(item))

    # Zip the package
    zip_name = 'Kodys_Foot_Clinik_Package.zip'
    print("Creating ZIP archive: {}...".format(zip_name))
    shutil.make_archive('Kodys_Foot_Clinik_Package', 'zip', dist_dir)
    
    print("Done! Distribution package created in 'Kodys_Foot_Clinik_Package.zip'")

if __name__ == "__main__":
    package_app()
