#! /usr/bin/python
"""
CleanUpFASTQ, a class for the clean up of FASTQ files.

Disclaimer: This has only been tested on Illumina reads.
"""
import random
import numpy as np


class CleanUpFASTQ(object):
    """Class for the clean up of FASTQ files."""

    def __init__(self, subsample, is_paired, read_length_cutoff,
                 min_mean_quality, min_read_length):
        """Initialize class variables."""
        self.VERSION = "0.5"
        self.fastq = []
        self.subsample = subsample
        self.is_paired = is_paired
        self.read_length_cutoff = read_length_cutoff
        self.min_mean_quality = min_mean_quality
        self.min_read_length = min_read_length
        self.__temp_read = []
        self.__phred64 = 0
        self.__phred33 = 0
        self.__phredunk = 0
        self.__contains_ns = 0
        self.__total_ns = 0
        self.__read_length = 0
        self.__bad_quality = 0
        self.__n_lengths = 0
        self.__missed_ns = 0

    def read_large_fastq(self, file, fraction):
        """Reduce a large (2 GB+) file to a subset before cleanup."""
        while 1:
            head = file.readline().rstrip()
            if not head:
                break

            seq = file.readline().rstrip()
            plus = file.readline().rstrip()
            qual = file.readline().rstrip()

            random.seed(123456)
            if random.random() <= fraction:
                self.fastq.append(head)
                self.fastq.append(seq)
                self.fastq.append(plus)
                self.fastq.append(qual)

                if self.is_paired:
                    self.fastq.append(file.readline().rstrip())
                    self.fastq.append(file.readline().rstrip())
                    self.fastq.append(file.readline().rstrip())
                    self.fastq.append(file.readline().rstrip())

    def __mean_quality(self, qual):
        """Create a count of the quality score."""
        qual_stats = np.array([ord(j) for j in qual])
        return np.mean(qual_stats) - 33

    def __get_nonambiguous_sequence(self, seq, qual):
        """Return the longest non-ambiguous sequence."""
        seqs = []
        new_seq = []
        quals = []
        new_qual = []
        for index, base in enumerate(seq):
            if base == 'N' and len(new_seq):
                seqs.append(''.join(new_seq))
                quals.append(''.join(new_qual))
                new_seq = []
                new_qual = []
            else:
                new_seq.append(base)
                new_qual.append(qual[index])

        if len(new_seq):
            seqs.append(''.join(new_seq))
            quals.append(''.join(new_qual))

        # Get the largest chunk
        new_seq = ''
        new_qual = ''
        for index, chunk in enumerate(seqs):
            if len(chunk) > len(new_seq):
                new_seq = chunk
                new_qual = quals[index]
            elif len(chunk) == len(new_seq):
                random.seed(123456)
                if random.random() <= 0.5:
                    new_seq = chunk
                    new_qual = quals[index]

        return [new_seq, new_qual]

    def __quality_trim(self, seq, qual):
        """Remove bases below minimum quality."""
        new_seq = []
        new_qual = []
        for index, base in enumerate(seq):
            q = ord(qual[index]) - 33
            if q < self.min_mean_quality and index >= self.min_read_length:
                break
            else:
                new_seq.append(base)
                new_qual.append(qual[index])

        return [''.join(new_seq), ''.join(new_qual)]

    def __test_read(self, index, append=''):
        """Test if the read passes quality filters."""
        head = self.fastq[index].split()[0]
        if append:
            if not head.endswith(append):
                head = "{0}{1}".format(self.fastq[index].split()[0], append)

        seq = self.fastq[index + 1]
        length = 0
        qual = self.fastq[index + 3]

        # If ambiguous nucleotides, get largest subsequence without
        # ambiguous nucleotides.
        if seq.count('N') > 0:
            seq, qual = self.__get_nonambiguous_sequence(seq, qual)
            self.__n_lengths += len(seq)
            self.__total_ns += seq.count('N')
            self.__contains_ns += 1

        if (seq.count('N') == 0 and len(seq) >= self.min_read_length):
            if (self.read_length_cutoff and length > self.read_length_cutoff):
                seq = seq[:self.read_length_cutoff]
                qual = qual[:self.read_length_cutoff]
            else:
                if (self.read_length_cutoff):
                    self.__read_length += 1

            if (self.__mean_quality(qual) >= self.min_mean_quality):
                self.__temp_read.append('{0}\n{1}\n+\n{2}'.format(
                    head,
                    seq,
                    qual
                ))
                length = len(seq)
            else:
                self.__bad_quality += 1
        else:
            self.__missed_ns += 1

        return length

    def generate_order(self, total_read_count):
        """Generate a random (seeded) order of reads to be selected."""
        if self.is_paired and total_read_count % 2 == 0:
            total_read_count = total_read_count / 2
        self.__read_order = range(total_read_count)
        if self.subsample:
            random.seed(123456)
            random.shuffle(self.__read_order)

    def clean_up_fastq(self):
        """Test each read, if good print it else move next read."""
        basepair_count = 0
        for i in xrange(len(self.__read_order)):
            self.__temp_read[:] = []
            if self.is_paired:
                index = self.__read_order[i] * 8 - 8
                read1 = self.__test_read(index, append="/1")
                index = self.__read_order[i] * 8 - 4
                read2 = self.__test_read(index, append="/2")
                if read1 > 0 and read2 > 0:
                    print('\n'.join(self.__temp_read))
                    basepair_count += (read1 + read2)
            else:
                index = self.__read_order[i] * 4 - 4
                read = self.__test_read(index)
                if read > 0:
                    print(self.__temp_read[0])
                    basepair_count += read

            if self.subsample and basepair_count >= self.subsample:
                break
        '''
        print('Ns: {0} ({3}, {5}) \tLength: {1}\tQual: {2}\tReads Saved: {4}'.format(
            self.__contains_ns, self.__read_length, self.__bad_quality,
            self.__total_ns, self.__n_lengths / float(self.__contains_ns),
            self.__missed_ns
        ))
        '''
