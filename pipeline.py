import os
import subprocess

def run_script(script_path):
    result = subprocess.run(["bash", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script_path}: {result.stderr}")
    else:
        print(f"Successfully ran {script_path}")

def submit_job(script_path):
    result = subprocess.run(["bsub", "<", script_path], shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error submitting job {script_path}: {result.stderr}")
    else:
        print(f"Successfully submitted job {script_path}")

def main():
    # Preprocessing
    submit_job("scripts/preprocessing/s1_run_intjob.sh")
    submit_job("scripts/preprocessing/s2_Merge_annotation.sh")
    
    # Feature extraction
    submit_job("scripts/feature_extraction/s3_Extract_PLP_PTV_variants.sh")
    
    # Filtering
    submit_job("scripts/filtering/s4_Filtering.PLP_s1.sh")
    submit_job("scripts/filtering/s4_Filtering.PLP_s2.sh")
    submit_job("scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh")
    submit_job("scripts/filtering/s6_filterExomesByVariants_PTV.sh")
    submit_job("scripts/filtering/s7_Getting_rare_PTV.sh")

    #Generate_summary_df_variants
    submit_job("scripts/summary/s8_Generate_summary_df.sh")

    submit_job("scripts/summary/s9_Cal_carrier_Freq.sh")


if __name__ == "__main__":
    main()
