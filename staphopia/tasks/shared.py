'''


'''
import os
import subprocess

def try_to_complete_task(test_this_file, touch_this_file):
    file_not_empty = False
    try:
        if os.stat(test_this_file).st_size > 0:
           file_not_empty = complete_task(touch_this_file)
        else:
           pass
    except OSError:
        pass
        
    return file_not_empty
        
def complete_task(filename):
    p = subprocess.Popen(['touch', filename], stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    return os.path.isfile(filename)
    
def find_and_remove_files(base_dir, name, min_depth='0', max_depth='99'):
    found_files = find_files(base_dir, name, min_depth, max_depth)
    if found_files:
        remove(found_files)
    
def find_files(base_dir, name, min_depth, max_depth):
    p = subprocess.Popen(['find', base_dir, '-mindepth', min_depth, 
                          '-maxdepth', max_depth, '-name', name], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')
    
def find_dirs(base_dir, name, min_depth, max_depth):
    p = subprocess.Popen(['find', base_dir, '-mindepth', min_depth, 
                          '-maxdepth', max_depth, '-type', 'd', '-name', name], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.split('\n')

def compress_and_remove(output_file, files, has_dirs=True):
    if has_dirs:
        if compress_dirs(output_file, files):
            remove(files)
            return True
        else:
            return False
    else:
        if compress_files(output_file, files):
            return True
        else:
            return False
    
def compress_dirs(output_file, files):
    cmd = ['tar', '-cf', '-']
    cmd.extend(filter(None, files))
    tar = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p = subprocess.Popen(['gzip', '--best'], stdin=tar.stdout,
                         stdout=open(output_file, 'w'))
    tar.wait()
    
    return os.path.isfile(output_file)
    
def remove(files):
    cmd = ['rm', '-rf']
    cmd.extend(files)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
def compress_files(files):
    for file in files:
        p = subprocess.Popen(['gzip', '--best', file], stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()