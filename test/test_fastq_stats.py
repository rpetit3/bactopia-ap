#! /usr/bin/env python
import subprocess
import unittest

def is_built(fastq):
    cat = subprocess.Popen(["cat", fastq], stdout=subprocess.PIPE)
    proc = subprocess.Popen(["../bin/fastq_stats"], stdin=cat.stdout,
                            stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    return out[0]

class is_valid_tests(unittest.TestCase):
    def testIsBuilt(self):
        self.assertIs(is_built('../test-data/test_valid.fastq'), '{')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
