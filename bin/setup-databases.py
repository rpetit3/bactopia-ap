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
    """For MentaLiST: Schemas available from www.cgmlst.org"""
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


def ariba_databases():
    """Print a list of databases available with 'ariba getref'."""
    getref_usage = ' '.join([
        line.strip() for line in
        execute('ariba getref --help', capture=True).strip().split('\n')
    ])
    databases = getref_usage.split('of: ')[1].split(' outprefix')[0]
    return databases.split()


def list_databases(ariba, pubmlst, missing=False):
    """Print available MLST and cgMLST schemas, and exit."""
    print_to = sys.stderr if missing else sys.stdout
    print("Preconfigured Ariba databases available:", file=print_to)
    print("\n".join(sorted(ariba)), file=print_to)

    print("\nMLST schemas available from pubMLST.org:", file=print_to)
    print("\n".join(sorted(pubmlst)), file=print_to)

    """
    Disabled until MentaLiST conda install is fixed
    print("\ncgMLST schemas available from cgMLST.org:", file=print_to)
    print("\n".join(sorted(cgmlst.keys())), file=print_to)
    """
    sys.exit(1 if missing else 0)


def setup_requests(request, available_databases, title):
    """Return a list of setup requests."""
    databases = []
    if os.path.exists(request):
        with open(request, 'r') is handle:
            for line in handle:
                database = line.rstrip()
                if database in available_databases:
                    databases.append(database)
                else:
                    logging.error(f'{data} is not available from {title}')
        return databases
    elif request in available_databases:
        databases.append(request)
    else:
        logging.error(f'{request} is not available from {title}')
    return databases


def setup_ariba(request, available_databases, outdir, force=False):
    """Setup each of the requested databases using Ariba."""
    requests = setup_requests(request, available_databases, 'ariba')
    if requests:
        ariba_dir = f'{outdir}/ariba'
        for request in requests:
            prefix = f'{ariba_dir}/{request}'
            if os.path.exists(prefix):
                if force:
                    logging.info(f'--force, removing existing {request} setup')
                    execute(f'rm -rf {prefix}')
                else:
                    logging.info(f'{request} ({prefix}) exists, skipping')
                    continue
            # Setup Ariba database
            logging.info(f'Setting up {request} Ariba database')
            fa = f'{prefix}.fa'
            tsv = f'{prefix}.tsv'
            execute(f'mkdir -p {ariba_dir}')
            execute(f'ariba getref {request} {prefix}')
            execute(f'ariba prepareref -f {fa} -m {tsv} {prefix}')
            execute(f'gzip -c {prefix}.fa > {prefix}/{request}.fa.gz')
            execute(f'gzip -c {prefix}.tsv > {prefix}/{request}.tsv.gz')
            execute(f'date > {prefix}/{request}-updated.txt')
    else:
        logging.info("No valid Ariba databases to setup, skipping")


def setup_mlst(request, available_databases, outdir, force=False):
    """Setup MLST databases for each requested schema."""
    requests = setup_requests(request, available_databases, 'pubMLST.org')
    if requests:
        for request in requests:
            species = request.lower().replace(' ', '_')
            mlst_dir = f'{outdir}/{species}/mlst'
            if os.path.exists(mlst_dir):
                if force:
                    logging.info(f'--force, removing existing {request} setup')
                    execute(f'rm -rf {mlst_dir}')
                else:
                    logging.info(f'{request} ({mlst_dir}) exists, skipping')
                    continue
            # Setup MLST database
            logging.info(f'Setting up MLST for {request}')
            execute(f'mkdir -p {mlst_dir}')

            # Ariba
            logging.info(f'Creating Ariba MLST database')
            ariba_dir = f'{mlst_dir}/ariba'
            execute(f'ariba pubmlstget "{request}" {ariba_dir}')
            execute('date > ariba-updated.txt', directory=ariba_dir)

            # BLAST
            logging.info(f'Creating BLAST MLST database')
            blast_dir = f'{mlst_dir}/blast'
            for fasta in glob.glob(f'{ariba_dir}/pubmlst_download/*.tfa'):
                output = os.path.splitext(fasta)[0]
                execute(f'makeblastdb -in {fasta} -dbtype nucl -out {output}')
            execute(f'mv {ariba_dir}/pubmlst_download {blast_dir}')
            execute('date > blast-updated.txt', directory=blast_dir)

            # MentaLiST
            logging.info(f'Creating MentaLiST MLST database')
            mentalist_dir = f'{mlst_dir}/mentalist'
            execute(f'mkdir -p {mentalist_dir}')
            execute((f'mentalist download_pubmlst -o mlst -k 31 -s "{request}"'
                     ' --db mlst.db'), directory=mentalist_dir)
            execute('date > mentalist-updated.txt', directory=mentalist_dir)

            # Finish up
            execute(f'date > {species}-updated.txt', directory=mlst_dir)
    else:
        logging.info("No valid MLST schemas to setup, skipping")


def setup_cgmlst(request, available_databases, outdir, force=False):
    """Setup cgMLST databases for each requested schema."""
    requests = setup_requests(request, available_databases, 'cgmlst.org')
    if requests:
        for request in requests:
            species = request.lower().replace(' ', '_')
            cgmlst_dir = f'{outdir}/{species}/cgmlst'
            if os.path.exists(cgmlst_dir):
                if force:
                    logging.info(f'--force, removing existing {request} setup')
                    execute(f'rm -rf {cgmlst_dir}')
                else:
                    logging.info(f'{request} ({cgmlst_dir}) exists, skipping')
                    continue
            # Setup MLST database
            logging.info(f'Setting up xgMLST for {request}')
            execute(f'mkdir -p {cgmlst_dir}')

            # MentaLiST
            logging.info(f'Creating MentaLiST MLST database')
            mentalist_dir = f'{cgmlst_dir}/mentalist'
            execute(f'mkdir -p {mentalist_dir}')
            execute((
                f'mentalist download_cgmlst -o cgmlst -k 31 -s "{request}" '
                '--db cgmlst.db'
            ), directory=mentalist_dir)

            # Finish up
            execute(f'date > {species}-updated.txt', directory=cgmlst_dir)
    else:
        logging.info("No valid cgMLST schemas to setup, skipping")



def set_log_level(error, debug):
    """Set the output log level."""
    return logging.ERROR if error else logging.DEBUG if debug else logging.INFO


def get_log_level():
    """Return logging level name."""
    return logging.getLevelName(logging.getLogger().getEffectiveLevel())


def execute(cmd, directory=os.getcwd(), capture=False):
    """ """
    from executor import ExternalCommand
    command = ExternalCommand(cmd, directory=directory, capture=True,
                              capture_stderr=True)
    command.start()
    if get_log_level() == 'DEBUG':
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
    parser.add_argument(
        '--ariba', metavar="ARIBA", type=str,
        help=('Setup Ariba database for a given database or a list of '
              'databases in a text file.')
    )
    parser.add_argument(
        '--mlst', metavar="MLST", type=str,
        help=('Download MLST schema for a given species or a list of species '
              'in a text file.')
    )
    parser.add_argument(
        '--cgmlst', metavar="CGMLST", type=str,
        help=('Download cgMLST schema for a given species or a list of '
              'species in a text file.')
    )
    parser.add_argument(
        '--outdir', metavar="OUTPUT_DIRECTORY", type=str,
        default='./', help='Directory to write output. (Default: ./)'
    )
    parser.add_argument(
        '--list_databases', action='store_true',
        help=('List resistance/virulence Ariba databases and (cg)MLST schemas '
              'available for setup.')
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
    logging.getLogger().setLevel(set_log_level(args.silent, args.verbose))
    validate_requirements()

    ARIBA_DATABASES = ariba_databases()
    PUBMLST_SCHEMAS = pubmlst_schemas()
    CGMLST_SCHEMAS = cgmlst_schemas()
    if args.list_databases:
        list_databases(ARIBA_DATABASES, PUBMLST_SCHEMAS, CGMLST_SCHEMAS)

    if args.ariba:
        logging.info('Setting up Ariba databases')
        setup_ariba(args.ariba, ARIBA_DATABASES, args.outdir, force=args.force)
    else:
        logging.info('No requests for an Ariba database, skipping')

    if args.mlst:
        logging.info('Setting up MLST databases')
        setup_mlst(args.mlst, PUBMLST_SCHEMAS, args.outdir, force=args.force)
    else:
        logging.info('No requests for an MLST schema, skipping')

    if args.cgmlst:
        logging.info('Setting up cgMLST databases')
        # Need mentalist conda install to be fixed
        # setup_cgmlst(args.cgmlst, CGMLST_SCHEMAS, args.outdir, force=args.force)
    else:
        logging.info('No requests for an cgMLST schema, skipping')
