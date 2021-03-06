#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import subprocess
import shlex
import shutil
import time
__author__ = 'xieguobi'

exclude_AppIcon = 'AppIcon.appiconset'
exclude_LaunchImage = 'LaunchImage.launchimage'
project_dir = "/your_path"
back_not_used_dir = "/your_path"
auto_delete = 0
auto_move = 0

def find_exclude_images():
    exclude_images_set = set()

    command = "find '{0}' -type d -name {other}".format(project_dir, other = exclude_AppIcon)
    s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = s.communicate()
    if len(result) > 0:
        exclude_path = result[0]

        for type in support_types():
            exclude_images_set = exclude_images_set | do_find_command(exclude_path,type)

    command = "find '{0}' -type d -name {other}".format(project_dir, other = exclude_LaunchImage)
    s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    result = s.communicate()
    if len(result) > 0:
        exclude_path = result[0]
        for type in support_types():
            exclude_images_set = exclude_images_set | do_find_command(exclude_path,type)

    return exclude_images_set

def do_find_command(search_dir,file_type):

    if len(search_dir) == 0 or len(file_type) == 0:
        return set()

    search_dir = search_dir.replace('\n','')
    all_names_set = set()
    command = "find '{}' -name '*.{other}' 2>/dev/null".format(search_dir,other = file_type)
    s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    results = s.communicate()[0].split()
    for name in results:

        if not name.endswith(file_type):
            continue

        head, tail = os.path.split(name)
        tail = os.path.splitext(tail)[0]

        if "@" in tail:
            all_names_set.add(tail.split('@')[0])
        else:
            all_names_set.add(tail)

    return all_names_set

def do_grep(path,key_word):

    if not is_available_file_path(path):
        print ('path:%s is not available' % path)
        return

    command = "grep -w -q '%s' '%s'" %(key_word,path)
    if subprocess.call(command, shell=True) == 0:
        return 1
    else:
        return 0

def goal_file(path):
    files = []
    for dirName, subdirList, fileList in os.walk(path):
                                    for fname in fileList:

                                            if is_available_file_path(fname):
                                                path = '%s/%s' % (dirName,fname)
                                                files.append(path)
    return files

def is_available_file_path(path):
    available = 0

    if path.endswith('.m'):
       available = 1
    if path.endswith('.h'):
       available = 1
    if path.endswith('.mm'):
        available = 1
    if path.endswith('.xib'):
        available = 1
    if path.endswith('.swift'):
        available = 1
    if path.endswith('.storyboard'):
        available = 1

    return available

def support_types():
    types = []
    types.append('png')
    types.append('jpg')
    types.append('jpeg')
    types.append('gif')
    return types

def delete_not_used_image(image):
    if len(image) == 0:
        return

    command = "find '{}' \( -name '{other1}' -o -name '{other2}@*' \) 2>/dev/null".format(project_dir,other1 = image,other2 = image)
    s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    results = s.communicate()[0].split()
    for path in results:

        valid = 0
        for type in support_types():
            if path.endswith(type):
                valid = 1
                break
        if valid:
            os.remove(path)
            print ('\r\n ========%s is deleted========' % image)

def move_not_used_image(image):
    if len(image) == 0:
        return

    command = "find '{}' \( -name '{other1}' -o -name '{other2}@*' \) 2>/dev/null".format(project_dir,other1 = image,other2 = image)
    s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    results = s.communicate()[0].split()
    for path in results:

        valid = 0
        for type in support_types():
            if path.endswith(type):
                valid = 1
                break
        if valid:
            filename, file_extension = os.path.splitext(path)
            des_dir = os.path.join(back_not_used_dir,"{}{}".format(image,file_extension))
            shutil.move(path,des_dir)
            print ('\r\n ========%s is moved========' % image)

def start_find_task():

    print("\nstart finding task...\nbelows are not used images:\n")
    global project_dir
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]

    if project_dir == " ":
        print("error! project_dir can not be nil")

    start = time.time()
    i = 0

    exclude_images_set = find_exclude_images()

    results = set()
    for type in support_types():
            results = results | do_find_command(project_dir,type)

    results = results - exclude_images_set

    goal_files = goal_file(project_dir)

    for image_name in results:

        used = 0
        for file_path in goal_files:

            if do_grep(file_path,image_name):
                used = 1
                # print ('image %s is used' % image_name)
                break

        if used == 0:
            print(image_name)
            i = i + 1
            if auto_delete:
                delete_not_used_image(image_name)
            elif auto_move:
                move_not_used_image(image_name)





    c = time.time() - start
    print('\nsearch finish,find %s results,total count %0.2f s'%(i,c))

start_find_task()
