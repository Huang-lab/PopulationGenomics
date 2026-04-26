import pandas as pd
import os


def calculate_carrier_frequencies(summary_df, patient_info_df, tag):
    """
    Calculates carrier frequencies at various levels (group, gene, ancestry, and ancestry-gene).

    Args:
    summary_df (DataFrame): Summary DataFrame containing variant information.
    patient_info_df (DataFrame): DataFrame containing patient information.
    tag (str): Label for this set of variants (e.g. 'plp' or 'ptv').

    Returns:
    dict: Dictionary with DataFrames for each frequency type.
    """
    # Ensure correct data types
    patient_info_df['MASKED_MRN'] = patient_info_df['MASKED_MRN'].astype(str)
    patient_info_df['Group'] = patient_info_df['Group'].astype(str)
    patient_info_df['genetically_determined'] = patient_info_df['genetically_determined'].astype(str)

    # Function to calculate frequency
    def calc_frequency(carriers, total):
        return (carriers / total * 100) if total > 0 else 0

    # 1. Whole cohort based on 'Group'
    total_by_group = patient_info_df['Group'].value_counts()
    group_freq = summary_df.groupby('Group')['PatientID'].nunique().reset_index(name='Num_carriers')
    group_freq['Num_samples'] = group_freq['Group'].map(total_by_group)
    group_freq['Num_noncarriers'] = group_freq['Num_samples'] - group_freq['Num_carriers']
    group_freq['Carrier_Freq'] = group_freq.apply(lambda row: calc_frequency(row['Num_carriers'], row['Num_samples']), axis=1)
    group_freq['Tag'] = tag
    group_freq = group_freq.sort_values('Carrier_Freq', ascending=False)

    # 2. Gene-level by Group
    gene_group_freq = summary_df.groupby(['Gene', 'Group'])['PatientID'].nunique().reset_index(name='Num_carriers')
    gene_group_freq['Num_samples'] = gene_group_freq['Group'].map(total_by_group)
    gene_group_freq['Num_noncarriers'] = gene_group_freq['Num_samples'] - gene_group_freq['Num_carriers']
    gene_group_freq['Carrier_Freq'] = gene_group_freq.apply(lambda row: calc_frequency(row['Num_carriers'], row['Num_samples']), axis=1)
    gene_group_freq['Tag'] = tag
    gene_group_freq = gene_group_freq.sort_values(['Gene', 'Carrier_Freq'], ascending=[True, False])

    # 3. Ancestry level by Group
    total_by_ancestry_group = patient_info_df.groupby(['genetically_determined', 'Group']).size().reset_index(name='Num_samples')
    ancestry_group_freq = summary_df.groupby(['genetically_determined', 'Group'])['PatientID'].nunique().reset_index(name='Num_carriers')
    ancestry_group_freq = ancestry_group_freq.merge(total_by_ancestry_group, on=['genetically_determined', 'Group'], how='right').fillna(0)
    ancestry_group_freq['Num_carriers'] = ancestry_group_freq['Num_carriers'].astype(int)
    ancestry_group_freq['Num_noncarriers'] = ancestry_group_freq['Num_samples'] - ancestry_group_freq['Num_carriers']
    ancestry_group_freq['Carrier_Freq'] = ancestry_group_freq.apply(lambda row: calc_frequency(row['Num_carriers'], row['Num_samples']), axis=1)
    ancestry_group_freq['Tag'] = tag
    ancestry_group_freq = ancestry_group_freq.sort_values(['genetically_determined', 'Group', 'Carrier_Freq'], ascending=[True, True, False])

    # 4. Ancestry-gene level by Group
    ancestry_gene_group_freq = summary_df.groupby(['genetically_determined', 'Gene', 'Group'])['PatientID'].nunique().reset_index(name='Num_carriers')
    ancestry_gene_group_freq = ancestry_gene_group_freq.merge(total_by_ancestry_group, on=['genetically_determined', 'Group'], how='left')
    ancestry_gene_group_freq['Num_noncarriers'] = ancestry_gene_group_freq['Num_samples'] - ancestry_gene_group_freq['Num_carriers']
    ancestry_gene_group_freq['Carrier_Freq'] = ancestry_gene_group_freq.apply(lambda row: calc_frequency(row['Num_carriers'], row['Num_samples']), axis=1)
    ancestry_gene_group_freq['Tag'] = tag
    ancestry_gene_group_freq = ancestry_gene_group_freq.sort_values(['genetically_determined', 'Group', 'Gene', 'Carrier_Freq'], ascending=[True, True, True, False])

    return {
        'group': group_freq,
        'gene_group': gene_group_freq,
        'ancestry_group': ancestry_group_freq,
        'ancestry_gene_group': ancestry_gene_group_freq
    }


def main():
    output_dir2 = '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/testout'
    patient_info_path = '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/metadata/Sema4_HX_WXS_Newgroups.tsv'

    patient_info_df = pd.read_csv(patient_info_path, sep='\t')

    # Read summary files for both tags
    summary_df = pd.read_csv(f'{output_dir2}/combined_summary.tsv', sep='\t')

    # Filter by tag
    summary_df_plp = summary_df[(summary_df['Tag'] == 'PLP') | (summary_df['Tag'] == 'PLP & PTV')]
    summary_df_ptv = summary_df[(summary_df['Tag'] == 'PTV') | (summary_df['Tag'] == 'PLP & PTV')]

    tags = {'plp': summary_df_plp, 'ptv': summary_df_ptv}

    for tag, df_tag in tags.items():
        # Calculate frequencies
        frequencies = calculate_carrier_frequencies(df_tag, patient_info_df, tag)

        # Save results
        for name, df in frequencies.items():
            output_file_path = os.path.join(output_dir2, f"{name}_frequencies_{tag}.tsv")
            df.to_csv(output_file_path, sep='\t', index=False)
            print(f"Saved {name} frequencies for {tag} to {output_file_path}")


if __name__ == "__main__":
    main()


