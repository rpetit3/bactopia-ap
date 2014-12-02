#! /usr/bin/python
'''
    Author: Robert A. Petit III

    [TODO: Elaborate on description]
'''
import random
import re
import numpy as np

class CleanUpFASTQ(object):

    def __init__(self, subsample, paired_reads, read_length_cutoff,
                 min_mean_quality, min_read_length):
        self.VERSION = "0.5"
        self.fastq = []
        self.subsample = subsample
        self.paired_reads = paired_reads
        self.read_length_cutoff = read_length_cutoff
        self.min_mean_quality = min_mean_quality
        self.min_read_length = min_read_length
        self.__temp_read = []
        self.__phred64 = 0
        self.__phred33 = 0
        self.__phredunk = 0

    def __mean_quality(self, qual):
        """Create a count of the quality score"""
        qual_stats = np.array([ord(j) for j in qual])
        return np.mean(qual_stats) - 33

    def __test_read(self, index):
        head = self.fastq[index]
        seq = self.fastq[index+1]
        length = 0
        qual = self.fastq[index+3]

        if (not re.search('N', seq) and len(seq) >= self.min_read_length):
            if (self.read_length_cutoff and length > self.read_length_cutoff):
                seq = seq[:self.read_length_cutoff]
                qual = qual[:self.read_length_cutoff]

            if (self.__mean_quality(qual) >= self.min_mean_quality):
                self.__temp_read.append('{0}\n{1}\n+\n{2}'.format(head,seq,qual))
                length = len(seq)

        return length

    def generate_order(self, total_read_count):
        if self.paired_reads and total_read_count % 2 == 0:
            total_read_count = total_read_count / 2

        self.__read_order = range(total_read_count)
        if self.subsample:
            random.seed(123456)
            random.shuffle(self.__read_order)

    def clean_up_fastq(self, ):
        basepair_count = 0

        for i in xrange(len(self.__read_order)):
            self.__temp_read[:] = []
            if self.paired_reads:
                index = self.__read_order[i] * 8 - 8
                read1 = self.__test_read(index)
                index = self.__read_order[i] * 8 - 4
                read2 = self.__test_read(index)
                if read1 > 0 and read2 > 0:
                    print '\n'.join(self.__temp_read)
                    basepair_count += (read1 + read2)
            else:
                index = self.__read_order[i] * 4 - 4
                read = self.__test_read(index)
                if read > 0:
                    print self.__temp_read[0]
                    basepair_count += read

            if self.subsample and basepair_count >= self.subsample:
                break
