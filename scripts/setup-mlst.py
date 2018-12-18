#! /usr/bin/env python3
# A wrapper for staphopia.nf, mainly for use on CGC.
import glob
import logging
import os
import sys
STDOUT = 11
STDERR = 12
logging.addLevelName(STDOUT, "STDOUT")
logging.addLevelName(STDERR, "STDERR")

def validate_requirements():
    """Validate the required programs are available, if not exit (1)."""
    from shutil import which
    programs = {
        'ariba': which('ariba'), 'makeblastdb': which('makeblastdb'),
        # 'mentalist': which('mentalist')
    }
    missing = [prog for prog, path in programs.items() if path is None]
    if missing:
        print("\n".join([m + ": command not found." for m in missing]),
              file=sys.stderr)
        print("Requirement missing, exiting", file=sys.stderr)
        sys.exit(1)


def cgmlst_schemas():
    """For Mentalist: Schemas available from www.cgmlst.org"""
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(urlopen('https://www.cgmlst.org/ncs'), "lxml")
    schemas = {}
    for link in soup.find_all('a'):
        address = link.get('href')
        # Example: https://www.cgmlst.org/ncs/schema/3956907/
        if 'schema' in address:
            schema_id = address.split('/')[-2]
            name = link.get_text().rstrip(" cgMLST")
            if "/" in name:
                genus, species = name.split()
                for s in species.split('/'):
                    schemas[f'{genus} {s}'] = schema_id
            else:
                schemas[name] = schema_id
    return schemas


def pubmlst_schemas():
    """Use Ariba to pull available MLST schemas from pubmlst.org"""
    return execute('ariba pubmlstspecies', capture=True).rstrip().split('\n')


def list_schemas(pubmlst, missing=False):
    """Print available MLST and cgMLST schemas, and exit."""
    print_to = sys.stderr if missing else sys.stdout
    print("MLST schemas available from pubMLST.org:", file=print_to)
    print("\n".join(sorted(pubmlst)), file=print_to)

    """
    Disabled until MentaLiST conda install is fixed
    print("\ncgMLST schemas available from cgMLST.org:", file=print_to)
    print("\n".join(sorted(cgmlst.keys())), file=print_to)
    """
    sys.exit(1 if missing else 0)


def log_level():
    """Return logging level name."""
    return logging.getLevelName(logging.getLogger().getEffectiveLevel())


def execute(cmd, directory=os.getcwd(), capture=False):
    """ """
    from executor import ExternalCommand
    command = ExternalCommand(cmd, directory=directory, capture=True,
                              capture_stderr=True)
    command.start()
    if log_level() == 'DEBUG':
        logging.log(STDOUT, command.decoded_stdout)
        logging.log(STDERR, command.decoded_stderr)

    if capture:
        return command.decoded_stdout


if __name__ == '__main__':
    import argparse as ap
    parser = ap.ArgumentParser(
        prog='setup-mlst.py',
        conflict_handler='resolve',
        description=('Setup MLST schema for a given organism.'))
    parser.add_argument('--species', metavar="SPECIES", type=str,
                        help=('Download MLST schema for a given species.'))
    parser.add_argument(
        '--outdir', metavar="OUTPUT_DIRECTORY", type=str,
        default='./', help='Directory to write output. (Default: ./)'
    )
    parser.add_argument(
        '--list_schemas', action='store_true',
        help='List (cg)MLST schemas available from pubmlst.org, or cgMLST.org.'
    )
    parser.add_argument('--verbose', action='store_true',
                        help='Print debug related text.')
    parser.add_argument('--silent', action='store_true',
                        help='Only critical errors will be printed.')
    parser.add_argument('--force', action='store_true',
                        help='Forcibly overwrite existing databases.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Setup logs
    FORMAT='%(asctime)s:%(name)s:%(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S',)
    if args.silent:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    validate_requirements()
    PUBMLST_SCHEMAS = pubmlst_schemas()
    CGMLST_SCHEMAS = None  # cgmlst_schemas()
    if args.list_schemas:
        list_schemas(PUBMLST_SCHEMAS, CGMLST_SCHEMAS)
    elif not args.species:
        print("'--species' or '--list_schemas' is required.", file=sys.stderr)
        sys.exit(1)

    species = args.species.lower().replace(' ', '_')
    mlst_dir = f'{args.outdir}/{species}/mlst'
    if os.path.exists(mlst_dir):
        if args.force:
            logging.info(f'--force used, removing existing database')
            execute(f'rm -rf {mlst_dir}')
        else:
            logging.error(
                f'{args.species} directory ({mlst_dir}) exists... exiting'
            )
            logging.error(
                f'Use "--force" to forcibly continue'
            )
            sys.exit(1)
    ariba_dir = f'{mlst_dir}/ariba'
    blast_dir = f'{mlst_dir}/blast'
    # mentalist_dir = f'{mlst_dir}/mentalist'

    if args.species not in PUBMLST_SCHEMAS:
        print(f'{args.species} schema not available from pubMLST.org',
              file=sys.stderr)
        list_schemas(PUBMLST_SCHEMAS, CGMLST_SCHEMAS, missing=True)

    execute(f'mkdir -p {mlst_dir}')
    logging.info(f'Setting up MLST for {args.species}')

    # Ariba
    logging.info(f'Creating Ariba MLST database')
    execute(f'ariba pubmlstget "{args.species}" {ariba_dir}')
    execute('date > ariba-updated.txt', directory=ariba_dir)

    # BLAST
    logging.info(f'Creating BLAST MLST database')
    for fasta in glob.glob(f'{ariba_dir}/pubmlst_download/*.tfa'):
        output = os.path.splitext(fasta)[0]
        execute(f'makeblastdb -in {fasta} -dbtype nucl -out {output}')
    execute(f'mv {ariba_dir}/pubmlst_download {blast_dir}')
    execute('date > blast-updated.txt', directory=blast_dir)

    """
    Disabled MentaLiST until Conda install fixed (2018-12-12)
    run_command(['mkdir', '-p', mentalist_dir])
    run_command(['mkdir', 'mlst', 'cgmlst'], cwd=mentalist_dir)
    run_command(
        ['mentalist', 'download_pubmlst', '-o', 'mlst/', '-s', args.species,
         '-k', '31', '--db mlst/mlst-31.db'], cwd=mentalist_dir
    )

    if args.species in CGMLST_SCHEMAS:
        logging.info(f'{args.species} cgMLST schema exists, downloading...')
        run_command(
            ['mentalist', 'download_cgmlst', '-o', 'cgmlst/',
             '-s', CGMLST_SCHEMAS[args.species],
             '-k', '31', '--db cgmlst/cgmlst-31.db'], cwd=mentalist_dir
        )
    else:
        logging.info(f'{args.species} cgMLST schema not found, skipping...')

    run_command(['date'], stdout='mentalist-updated.txt', cwd=mentalist_dir)
    """
