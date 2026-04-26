import gzip
import os
import pandas as pd


def read_vcf_to_dataframe(path_vcf):
    if path_vcf.endswith('.gz'):
        open_func = gzip.open
        mode = 'rt'
    else:
        open_func = open
        mode = 'r'

    with open_func(path_vcf, mode) as file:
        while True:
            pos = file.tell()
            line = file.readline()
            if not line.startswith('##'):
                file.seek(pos)
                break

        vcf_df = pd.read_csv(file, sep='\t')

    return vcf_df


def transform_for_annovarV2(ref, alt):
    # VCF '*' alt = spanning deletion from an upstream allele; ANNOVAR
    # tables don't represent these, so leave them alone.
    if alt == '*':
        return ref, alt
    if len(ref) > 1 and len(alt) == 1 and ref[0] == alt:
        return ref[1:], "-"
    if len(ref) == 1 and len(alt) > 1 and alt[0] == ref:
        return "-", alt[1:]
    return ref, alt


def read_variant_table(variant_file):
    variants = set()
    with open(variant_file, 'r') as file:
        for line in file:
            if line.startswith("#"):
                continue
            parts = line.strip().split('\t')
            chrom, pos, ref, alt = parts[:4]
            variant_key = (chrom, pos, ref, alt)
            variants.add(variant_key)
    return variants


def filter_vcf(vcf_file, annovar_variants, output_vcf_path):
    open_func = gzip.open if vcf_file.endswith('.gz') else open
    with open_func(vcf_file, 'rt') as vcf, open(output_vcf_path, 'w') as out_vcf:
        for line in vcf:
            if line.startswith("#"):
                out_vcf.write(line)
                continue
            parts = line.strip().split('\t')
            chrom, pos, _, ref, alts = parts[:5]
            alt = alts.split(',')[0]
            transformed_ref, transformed_alt = transform_for_annovarV2(ref, alt)
            if (chrom, pos, transformed_ref, transformed_alt) in annovar_variants:
                out_vcf.write(line)


def main():
    input_vcf = os.environ['input_vcf']
    variants = os.environ['variants']
    output_vcf = os.environ['output_vcf']

    variants_site = read_variant_table(variants)
    filter_vcf(input_vcf, variants_site, output_vcf)


if __name__ == "__main__":
    main()
