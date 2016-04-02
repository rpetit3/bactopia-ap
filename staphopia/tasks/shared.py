"""A group of shared methods between tasks."""
import os
import subprocess


def gziplines(fname):
    """Use zcat to deliver lines from gzipped input."""
    f = subprocess.Popen(['zcat', fname], stdout=subprocess.PIPE)
    for line in f.stdout:
        yield line


def run_command(cmd, stdout=False, stderr=False, verbose=True):
    """
    Execute a single command and return STDOUT and STDERR.

    If stdout or stderr are given, output will be written to given file name.
    """
    cmd = filter(None, cmd)
    if verbose:
        print ' '.join(cmd)
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)

    return p.communicate()


def pipe_command(cmd_1, cmd_2, stdout=False, stderr=False):
    """
    Pipe two commands and return STDOUT and STDERR.

    If stdout or stderr are given, output will be written to given file name.
    """
    cmd_1 = filter(None, cmd_1)
    cmd_2 = filter(None, cmd_2)
    print '{0} | {1}'.format(' '.join(cmd_1), ' '.join(cmd_2))

    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p1 = subprocess.Popen(cmd_1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin=p1.stdout, stdout=stdout, stderr=stderr)
    p1.wait()

    return p2.communicate()


def pipe_commands(cmd_1, cmd_2, cmd_3, stdout=False, stderr=False):
    """Pipe three commands and return STDOUT and STDERR.

    If stdout or stderr are given, output will be written to given file name.
    """
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    cmd_1 = filter(None, cmd_1)
    cmd_2 = filter(None, cmd_2)
    cmd_3 = filter(None, cmd_3)
    print '{0} | {1} | {2}'.format(
        ' '.join(cmd_1), ' '.join(cmd_2), ' '.join(cmd_3)
    )
    p1 = subprocess.Popen(cmd_1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(cmd_3, stdin=p2.stdout, stdout=stdout, stderr=stderr)
    p1.wait()

    return p3.communicate()


def find_and_remove_files(base_dir, name, min_depth='0', max_depth='99'):
    """Find files within a directory matching a given name and delete them."""
    found_files = find_files(base_dir, name, min_depth, max_depth)
    if found_files:
        remove(found_files)


def find_files(base_dir, name, min_depth, max_depth):
    """
    Find files in a directory matching a given name.

    Return a list of the results.
    """
    stdout, stderr = run_command(
        ['find', base_dir, '-mindepth', min_depth, '-maxdepth', max_depth,
         '-name', name]
    )

    return stdout.split('\n')


def find_dirs(base_dir, name, min_depth, max_depth):
    """Find directories matching a given name. Return a list of the results."""
    stdout, stderr = run_command(
        ['find', base_dir, '-mindepth', min_depth, '-maxdepth', max_depth,
         '-type', 'd', '-name', name]
    )
    return stdout.split('\n')


def compress_and_remove(output_file, files, tarball=True):
    """Compress files with tar and gzip, or compress each file using gzip."""
    if tarball:
        if create_tar_gz(output_file, files):
            remove(files)
            return True
        else:
            return False
    else:
        gzip_files(files)
        return True


def create_tar_gz(output_file, files):
    """Create tarball and compress it using gzip."""
    pipe_command(
        ['tar', '-cf', '-'] + filter(None, files),
        ['gzip'],
        stdout=output_file
    )

    return os.path.isfile(output_file)


def gzip_files(files):
    """Compress a list of files with gzip."""
    for file in files:
        run_command(['gzip', file])


def remove(files):
    """Delete a list of files."""
    run_command(['rm', '-rf'] + files)


def get_md5sum(file):
    """Return the MD5SUM of an input file."""
    stdout, stderr = run_command(['md5sum', file], verbose=False)
    if stdout:
        md5sum, filename = stdout.split()
        return md5sum
    else:
        return None
