'''
    Author: Robert A Petit III
    
    A group of shared methods between tasks.
'''
import os
import subprocess

def run_command(cmd, stdout=False, stderr=False):
    '''
    Execute a single command and return STDOUT and STDERR. If stdout or stderr 
    are given, output will be written to given file name. 
    '''
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
    p.wait()
    
    return p.communicate()
    
def pipe_command(cmd_1, cmd_2, stdout=False, stderr=False):
    '''
    Pipe two commands and return STDOUT and STDERR.  If stdout or stderr are 
    given, output will be written to given file name.
    '''
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p1 = subprocess.Popen(cmd_1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin=p1.stdout, stdout=stdout, stderr=stderr)
    p1.wait()
    
    return p2.communicate()
    
def pipe_commands(cmd_1, cmd_2, cmd_3, stdout=False, stderr=False):
    '''
    Pipe three commands and return STDOUT and STDERR.  If stdout or stderr are 
    given, output will be written to given file name.
    '''
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p1 = subprocess.Popen(cmd_1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd_3, stdin=p2.stdout, stdout=stdout, stderr=stderr)
    p1.wait()
    
    return p3.communicate()
    
def try_to_complete_task(test_this_file, touch_this_file):
    '''
    Test to make sure a file exists and is not empty before completing a task.
    '''
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
    '''
    Create file marking task as complete for Ruffus purposes.
    '''
    touch = run_command(['touch', filename])
    
    return os.path.isfile(filename)
    
def find_and_remove_files(base_dir, name, min_depth='0', max_depth='99'):
    '''
    Find files within a directory matching a given name and delete them.
    '''
    found_files = find_files(base_dir, name, min_depth, max_depth)
    if found_files:
        remove(found_files)
    
def find_files(base_dir, name, min_depth, max_depth):
    '''
    Find files in a directory matching a given name. Return a list of the 
    results.
    '''
    stdout, stderr = run_command(
        ['find', base_dir, '-mindepth', min_depth, '-maxdepth', max_depth, 
         '-name', name]
    )
    
    return stdout.split('\n')
    
def find_dirs(base_dir, name, min_depth, max_depth):
    '''
    Find directories matching a given name. Return a list of the results.
    '''
    stdout, stderr = run_command(
        ['find', base_dir, '-mindepth', min_depth, '-maxdepth', max_depth, 
         '-type', 'd', '-name', name]
    )
    
    return stdout.split('\n')

def compress_and_remove(output_file, files, tarball=True):
    '''
    Compress files with tar and gzip, or compress each file using gzip.
    '''
    if tarball:
        if create_tar_gz(output_file, files):
            remove(files)
            return True
        else:
            return False
    else:
        if gzip_files(output_file, files):
            return True
        else:
            return False
    
def create_tar_gz(output_file, files):
    '''
    Create tarball and compress it using gzip
    '''
    tar_gz = pipe_command(
        ['tar', '-cf', '-'] + filter(None, files),
        ['gzip', '--best'],
        stdout=output_file
    )
    
    return os.path.isfile(output_file)
    
def gzip_files(files):
    '''
    Compress a list of files with gzip
    '''
    for file in files:
        gzip = run_command(['gzip', '--best', file])
        
def remove(files):
    '''
    Delete a list of files
    '''
    rm = run_command(['rm', '-rf'] + files)

    