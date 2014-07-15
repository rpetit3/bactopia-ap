#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <algorithm>
#include <vector>
#include <math.h>
#include <sstream>
using namespace std;
const int MAX_READ_LENGTH = 50000;
const float GENOME_SIZE = 2814816.0;

class Stats {
    public: 
        // Read stats
        vector<unsigned int> read_length;
        unsigned long int total_reads;
        unsigned long int total_bp;
        unsigned int min_read_length;
        unsigned int max_read_length;
        float avg_read_length;
        
        // Qual stats
        vector<double> per_read_qual;
        vector<unsigned int> per_base_qual;
        vector<unsigned int> per_base_count;
        int phred;
        double qual_sum;
        double qual_mean;
        double qual_median;
        double qual_25th;
        double qual_75th;
        double qual_std;
        
        // JSON output
        ostringstream json;
        
        void init(void) {
            total_reads = 0;
            total_bp = 0;
            qual_sum = 0;
            per_base_qual.resize(MAX_READ_LENGTH,0);
            per_base_count.resize(MAX_READ_LENGTH,0);
            phred = 33;
        }

        void transform_quality(string qual) {
            unsigned int total = 0;
            for (unsigned int i = 0; i < qual.length(); i++) {
                unsigned int qual_val = (unsigned int)qual[i]-phred;
                per_base_qual[i] += qual_val;
                per_base_count[i]++;
                total += qual_val;
            }
            double avg_qual = total / qual.length();
            qual_sum += avg_qual;
            per_read_qual.push_back(avg_qual);
        }

        void read_stats(void) {
            min_read_length = read_length[0];
            max_read_length = min_read_length;
            total_bp = 0;
            for(std::vector<unsigned int>::iterator j=read_length.begin();j!=read_length.end();++j) {
                if (*j > max_read_length) {
                    max_read_length = *j;
                } else if (*j < min_read_length) {
                    min_read_length = *j;
                }
                total_bp += *j;
            }
            
            avg_read_length = total_bp / float(total_reads);
        }
        
        void qual_stats(void) {
            qual_mean = qual_sum / total_reads;
            double temp = 0;
            for (unsigned int i = 0; i < total_reads; i++) {
                temp += (per_read_qual[i] - qual_mean) * (per_read_qual[i] - qual_mean);
            }
            qual_std = sqrt(temp / total_reads);
            
            size_t size = per_read_qual.size();
            sort(per_read_qual.begin(), per_read_qual.end());

            if (size % 2 == 0) {
                qual_25th = (per_read_qual[size / 4 - 1] + per_read_qual[size / 4]) / 2.0;
                qual_median = (per_read_qual[size / 2 - 1] + per_read_qual[size / 2]) / 2.0;
                qual_75th = (per_read_qual[int(size * 0.75 - 1)] + per_read_qual[int(size * 0.75)]) / 2.0;
            }
            else {
                qual_25th = per_read_qual[size / 4];
                qual_median = per_read_qual[size / 2];
                qual_75th = per_read_qual[int(size * 0.75)];
            }
        }
        
        void jsonify_stats(void) {
            json << "{";
            json << "\"total_bp\":" << total_bp << ",";
            json << "\"total_reads\":" << total_reads << ",";
            json << "\"coverage\":" << total_bp / GENOME_SIZE << ",";
            json << "\"min_read_length\":" << min_read_length << ",";
            json << "\"avg_read_length\":" << avg_read_length << ",";
            json << "\"max_read_length\":" << max_read_length << ",";
            json << "\"qual_mean\":" << qual_mean << ",";
            json << "\"qual_std\":" << qual_std << ",";
            json << "\"qual_median\":" << qual_median << ",";
            json << "\"qual_25th\":" << qual_25th << ",";
            json << "\"qual_75th\":" << qual_75th;
            json << "}";
        }
        
        void print_stats(void) {
            cout << json.str() << endl;
            cout << "Mean Phred Quality By Position Index" << endl;
            cout << "Position\tMean Quality" << endl;
            for (unsigned int i = 0; i < max_read_length; i++) {
                cout << i << "\t" << per_base_qual[i] / float(per_base_count[i]) << endl;
            }
            cout << "Overall Mean Phred Quality: " << setprecision(5) << qual_mean << " (s.d. " << qual_std << ")" << endl;
            cout << "Overall Median Phred Quality: " << setprecision(5) << qual_median << endl;
            cout << "Overall 25th Percentile Phred Quality: " << setprecision(5) << qual_25th << endl;
            cout << "Overall 75th Percentile Phred Quality: " << setprecision(5) << qual_75th << endl;
            cout << "Total Basepairs: " << total_bp << endl;
            cout << "Total Reads: " << total_reads << endl;
            cout << "Mean Read Length: " << avg_read_length << endl;
            cout << "Minimum Read Length: " << min_read_length << endl;
            cout << "Maximum Read Length: " << max_read_length << endl;
            cout << "Estimated Coverage: " << total_bp / GENOME_SIZE << endl;
        }
};

int main(int argc,char **argv) {
    Stats stats;
    stats.init();
    string name, seq, plus, qual;
    ifstream in("/dev/stdin", ios::in);
    while(true) {
        if(!getline(in,name,'\n')) break;
        if(!getline(in,seq,'\n')) break;
        if(!getline(in,plus,'\n')) break;
        if(!getline(in,qual,'\n')) break;
        stats.read_length.push_back(seq.length());
        stats.total_reads++;
        stats.transform_quality(qual);
    }
    in.close();
    
    // Determine Stats
    stats.read_stats();
    stats.qual_stats();
    stats.jsonify_stats();
    stats.print_stats();
    return 0;
}
