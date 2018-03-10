from distutils.dir_util import copy_tree
from subprocess import call
from tempfile import mkstemp
import os
import shutil
import sys
import urllib

CWD=os.getcwd()

def get_configs(requestID):
    f = open('config.txt', 'r')
    print 'Reading from config.txt'
    for line in f:
        if "SHORTCUT_APP_TEMPLATE_DIR=" in line:
            srcDir = CWD+line[26:].strip()
            wrkDir='./factory/'+requestID
        if "ANDROID_SDK_DIR=" in line:
            sdkDir = line[16:].strip()
        if "ANDROID_RETROARCH_DIR=" in line:
            retroDir = line[22:].strip()
        if "LIBRETRO_DICT=" in line:
            libretroDict = eval(line[14:].strip())
    return [srcDir,wrkDir,sdkDir,retroDir,libretroDict]

def write_keys():
    print 'Using production keys'
    keys = open('keys.txt', 'r')
    replace('./temp_apk/app/build.gradle', 
            'storeFile file("myreleasekey.keystore")',
            keys.readline().strip())
    replace('./temp_apk/app/build.gradle', 
            'storePassword "password"',
            keys.readline().strip())
    replace('./temp_apk/app/build.gradle', 
            'keyAlias "MyReleaseKey"',
            keys.readline().strip())
    replace('./temp_apk/app/build.gradle', 
            'keyPassword "password"',
            keys.readline().strip())

def clone_sourcecode(srcdir,wrkdir):
    copy_tree(srcdir, wrkdir)
    # Remove build and IDE-specific files
    try:
        shutil.rmtree(wrkdir+'/.idea')
    except:
        pass
    try:
        shutil.rmtree(wrkdir+'/build')
    except:
        pass

def compile_app(packageName,requestID):
    # Change our local properties
    f = open('config.txt', 'r')
    print 'Reading from config.txt'
    for line in f:
        if "ANDROID_SDK_DIR=" in line:
            uri = line[16:].strip()
            localProperties = open(wrkDir+'/local.properties', 'w')
            localProperties.write('sdk.dir=' + uri)
            os.environ['ANDROID_HOME'] = uri
            print 'Android SDK location set to ' + uri
    # Once everything is good, program from cmd line
    # call(['./temp_apk/gradlew'])
    print 'Building APK...'
    with open(wrkDir+'/app/src/main/res/values/strings.xml', 'r') as fin:
        print fin.read()
    # Is it good? Let's assume so
    os.chdir('temp_apk/');
    if len(sys.argv) > 2 and sys.argv[2] == '--windows':
        os.system('gradlew clean --info')
        os.system('gradlew assembleRelease')
    else:
        call(['./gradlew', 'clean'])
        call(['./gradlew', 'assembleRelease'])
        
    os.chdir('../');
    upload_apk(packageName)
    
def upload_apk(packageName,requestID):
    # Move to deliverable directory
    print 'APK created.'
    shutil.move(wrkDir+'/app/build/outputs/apk/app-release.apk', './deliverable/launch_' + packageName + '.' + requestId + '.apk')
    print 'Apk uploaded successfully'
            
#def generate_apk(appName, gameName, emuPackageName, emuClassName, callAction, banner):
def generate_apk(appName, gameType, emuPackageName, emuClassName, bannerDir,requestID):
    # Format variables
    gameName=appName.lower().replace(' ','')
    romName=gameName if gameType=="arcade" else "rom"
    if gameType=="arcade":
        romExt=".zip"
    elif gameType=="segamd":
        romExt=".bin"
    else:
        romExt="."+gameType
    # Get config variables
    [srcDir,wrkDir,sdkDir,retroDir,libretroDict]=get_configs(requestID)
    clone_sourcecode(srcDir,wrkDir)
    # Cook app/build.gradle
    cook(wrkDir+'/app/build.gradle',
    ['applicationId "toBeModified"','applicationId "games.androidtv.shortcut.'+gameType+'.'+gameName+'"'])
    # Cook Manifest
    cook(wrkDir+'/app/src/main/AndroidManifest.xml',
    [['package="toBeModified"','package="games.androidtv.shortcut.' + gameType + '.' + gameName + '"'],
    ['android:banner="@drawable/tv_banner_x"','android:banner="@drawable/tv_banner"']])
    # Cook MainActivity
    cook(wrkDir+'/app/src/main/java/games/androidtv/shortcut/MainActivity.java',
    [['import toBeModified.R;','import games.androidtv.shortcut.' + gameType + '.' + gameName + '.R;'],
    ['String gameName="ToBeModified";','String gameName="' + gameName + '";'],
    ['String gameType="ToBeModified";','String gameType="' + gameType + '";'],
    ['String emuName="ToBeModified";','String emuName="' + emuPackageName + '";'],
    ['String emuClass="ToBeModified";','String emuClass="' + emuClassName + '";'],
    ['String romFilename="ToBeModified";','String romFilename="' + romName + romExt + '";'],
    ['intent.putExtra("LIBRETRO","ToBeModified");','intent.putExtra("LIBRETRO","' + retroDir + libretroDict[gameType] + '");']])
    # Cook strings.xml
    cook(wrkDir+'/app/src/main/res/values/strings.xml',
    [['app_name">','app_name">'+appName],
    ['package_name">','package_name">'+emuPackageName + '.' + gameType + '.' + gameName]])
    # Download banner to ./temp_apk/app/src/main/res/drawable
    # FIXME Make sure this is a png, issue an error if not
    urllib.urlretrieve(bannerDir+'/'+gameName+'.png', wrkDir+'/app/src/main/res/drawable/tv_banner.png')
    urllib.urlretrieve(bannerDir+'/'+gameName+romExt, wrkDir+'/app/src/main/assets/'+romName+romExt)
    # Compile
    print 'Compiling app ' + emuPackageName + '.' + gameType + '.' + gameName
    compile_app(emuPackageName + '.' + gameType + '.' + gameName)

def cook(file_path, pattern_list):
    #C reate temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                for p in pattern_list:
                    if p[0] in line:
                        line=line.replace(p[0],p[1])
                        pattern_list.remove(p)
                new_file.write(line)
    os.close(fh)
    # Remove original file
    os.remove(file_path)
    # Move new file
    print "Temporarily copied file to " + abs_path
    print "Rewriting file at " + file_path
    shutil.move(abs_path, file_path)