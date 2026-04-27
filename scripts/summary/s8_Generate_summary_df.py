#!/usr/bin/env python
# coding: utf-8



import gzip
import logging
from pathlib import Path

import pandas as pd


def read_vcf_to_dataframe(path_vcf):
    open_func = gzip.open if path_vcf.endswith('.gz') else open
    mode = 'rt' if path_vcf.endswith('.gz') else 'r'
    
    with open_func(path_vcf, mode) as file:
        for line in file:
            if not line.startswith('##'):
                header = line.strip().split('\t')
                break
        
        df = pd.read_csv(file, sep='\t', names=header, comment='#')
    
    return df

def load_gene_info(file_path):
    gene_info = pd.read_csv(file_path, sep='\t')
    return dict(zip(zip(gene_info['#CHROM'], gene_info['POS']), gene_info['Ref.Gene']))

def annotate_vcf_with_gene(vcf_df, gene_info, output_path):
    """Add a Ref.Gene column from a (CHROM, POS) -> gene mapping.

    Args:
        vcf_df: VCF DataFrame to annotate.
        gene_info: dict keyed by (CHROM, POS) returning the gene symbol.
        output_path: where to write the annotated TSV.

    Returns:
        The annotated DataFrame, with Ref.Gene placed at column index 5
        (right after CHROM/POS/ID/REF/ALT). Missing positions get '.'.
    """
    if gene_info:
        gene_df = pd.DataFrame(
            [(c, p, g) for (c, p), g in gene_info.items()],
            columns=['#CHROM', 'POS', 'Ref.Gene'],
        )
        vcf_df = vcf_df.merge(gene_df, on=['#CHROM', 'POS'], how='left')
    else:
        vcf_df = vcf_df.copy()
        vcf_df['Ref.Gene'] = pd.NA
    vcf_df['Ref.Gene'] = vcf_df['Ref.Gene'].fillna('.')

    last_col = vcf_df.pop(vcf_df.columns[-1])
    vcf_df.insert(5, last_col.name, last_col)

    vcf_df.to_csv(output_path, sep='\t', index=False)
    return vcf_df




def is_carrier(genotype):
    """Return 1 if the sample carries at least one alt allele, else 0.

    Handles unphased ('/') and phased ('|') genotypes, missing calls ('.'),
    and the FORMAT field's colon-separated extras. Hom-alt ('1/1', '1|1') and
    multi-allelic alt indices ('1/2') all count as carriers.
    """
    if genotype is None:
        return 0
    gt = str(genotype).split(':', 1)[0]
    if not gt or gt == '.':
        return 0
    alleles = gt.replace('|', '/').split('/')
    for a in alleles:
        if a not in ('', '.', '0'):
            return 1
    return 0


def process_vcf(vcf_df, tag, patient_info_df):
    # Drop redundant columns
    df = vcf_df.drop(columns=['QUAL', 'ID', 'FILTER', 'INFO', 'FORMAT'])

    # Melt the DataFrame to unpivot the patient columns
    df_melted = df.melt(id_vars=['#CHROM', 'POS', 'REF', 'ALT', 'Ref.Gene'], var_name='PatientID', value_name='Genotype')

    # Convert 'PatientID' to string for comparison
    df_melted['PatientID'] = df_melted['PatientID'].astype(str)

    # Identify carriers
    df_melted['Carrier'] = df_melted['Genotype'].apply(is_carrier)
    
    # Filter to keep only rows where Carrier is greater than 0
    df_melted_carrier = df_melted[df_melted['Carrier'] > 0]
    
    # Merge with patient info to get additional details
    df_summary = df_melted_carrier.merge(patient_info_df, left_on='PatientID', right_on='MASKED_MRN')
    
    # Rename 'Ref.Gene' to 'Gene'
    df_summary.rename(columns={'Ref.Gene': 'Gene'}, inplace=True)
    
    # Add tag column
    df_summary['Tag'] = tag
    
    return df_summary


def create_summary_table(plp_vcf_path, ptv_vcf_path, patient_info_df):
    # Ensure 'MASKED_MRN' in patient_info_df is string type
    patient_info_df['MASKED_MRN'] = patient_info_df['MASKED_MRN'].astype(str)
    
    # Read VCF files
    plp_vcf_df = read_vcf_to_dataframe(plp_vcf_path)
    ptv_vcf_df = read_vcf_to_dataframe(ptv_vcf_path)
    
    log = logging.getLogger("s8")
    log.info("processing PLP VCF")
    plp_results = process_vcf(plp_vcf_df, 'PLP', patient_info_df)

    log.info("processing PTV VCF")
    ptv_results = process_vcf(ptv_vcf_df, 'PTV', patient_info_df)
    
    # Combine results
    all_results = pd.concat([plp_results, ptv_results])
    
    # Create a unique identifier for each variant-patient combination
    all_results['variant_patient'] = all_results.apply(lambda row: f"{row['#CHROM']}_{row['POS']}_{row['REF']}_{row['ALT']}_{row['PatientID']}", axis=1)
    
    # Identify overlaps
    overlap_mask = all_results.duplicated(subset=['variant_patient'], keep=False)
    all_results.loc[overlap_mask, 'Tag'] = 'PLP & PTV'
    
    # Remove duplicate entries, keeping 'PLP & PTV' when present
    all_results = all_results.sort_values('Tag').drop_duplicates(subset=['variant_patient'], keep='last')
    
    # Remove the temporary 'variant_patient' column
    all_results = all_results.drop('variant_patient', axis=1)
    
    # Add PLPorPTV_carrier column
    #all_results['PLPorPTV_carrier'] = 'Carrier'
    
    # Ensure specified columns are strings. The cohort schema uses 'Group'
    # for the cohort label and 'genetically_determined' for ancestry; keep
    # both in sync with s9_Cal_carrier_Freq.py.
    string_columns = [
        'PERS_HX_SMOKING', 'PERS_HX_CANCER', 'FAMILY_HX_CANCER', 'PersHisMN',
        'FamHisPMN', 'Group', 'genetically_determined', 'Tag',
        'MASKED_MRN', 'PatientID',
    ]
    for col in string_columns:
        if col in all_results.columns:
            all_results[col] = all_results[col].astype(str)
    
    # Sort the results
    all_results = all_results.sort_values(['#CHROM', 'POS', 'REF', 'ALT', 'PatientID'])
    
    return plp_results, ptv_results, all_results


 





def main():
    import logging
    import os
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger("s8")

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    import config

    paths = config.stage8_paths()
    os.makedirs(paths.output_dir, exist_ok=True)

    log.info("reading PLP VCF: %s", paths.plp_vcf)
    plp_vcf_df = read_vcf_to_dataframe(str(paths.plp_vcf))
    log.info("reading PTV VCF: %s", paths.ptv_vcf)
    ptv_vcf_df = read_vcf_to_dataframe(str(paths.ptv_vcf))
    plp_gene_info = load_gene_info(str(paths.plp_gene_info))
    ptv_gene_info = load_gene_info(str(paths.ptv_gene_info))
    patient_info_df = pd.read_csv(paths.patient_info, sep='\t')

    plp_annotated_path = paths.output_dir / "plp_annotated.vcf"
    ptv_annotated_path = paths.output_dir / "ptv_annotated.vcf"

    annotate_vcf_with_gene(plp_vcf_df, plp_gene_info, str(plp_annotated_path))
    annotate_vcf_with_gene(ptv_vcf_df, ptv_gene_info, str(ptv_annotated_path))

    plp_sum, ptv_sum, summary_df = create_summary_table(
        str(plp_annotated_path), str(ptv_annotated_path), patient_info_df
    )

    ptv_sum.to_csv(paths.output_dir / "summary.ptv.tsv", sep='\t', index=False)
    plp_sum.to_csv(paths.output_dir / "summary.plp.tsv", sep='\t', index=False)
    summary_df.to_csv(paths.output_dir / "combined_summary.tsv", sep='\t', index=False)
    log.info("wrote summary outputs to %s", paths.output_dir)


if __name__ == "__main__":
    main()


