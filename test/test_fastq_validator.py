#! /usr/bin/env python
import subprocess
import unittest

def is_valid(fastq):
    proc = subprocess.Popen(["../bin/fastq_validator", "--quiet", "--file", 
                            fastq], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    return out[0]

class is_valid_tests(unittest.TestCase):
    def testValid(self):
        self.assertIs(is_valid('../test-data/test_valid.fastq'), '0')

    def testInValid(self):
        self.assertIs(is_valid('../test-data/test_invalid.fastq'), '1')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
