from scores import DBConnector, ScoreCalculator
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

# Instantiate an object of DBConnector class
db = DBConnector(host="localhost", username="hussam", password="abcd123?", database="wire")

# Load tables of interest from the db as pandas dfs
candidate_df, degree_bsc_df, degree_master_df, dergee_phd_df,\
teaching_exp_df, industry_exp_df, patents_df, supervision_bsc_df,\
supervision_masters_df, supervision_phd_df, committee_work_df,\
quality_accreditation_df, certificates_df, awards_df,funded_research_df,citation_df = db.load_tables()

# Instantiate ScoreCalculator class
calculate_score = ScoreCalculator(db.host, db.username, db.password, db.database,candidate_df,
                                degree_bsc_df, degree_master_df, dergee_phd_df, teaching_exp_df,
                                industry_exp_df, patents_df,supervision_bsc_df, supervision_masters_df,
                                supervision_phd_df,committee_work_df, quality_accreditation_df,
                                certificates_df, awards_df, funded_research_df,citation_df)

# Calculate university ranking based candidate scores
uni_ranking_scores = calculate_score.university_score()

# Calculate teaching expereince based candidate score
teaching_exp_scores = calculate_score.teaching_expereince_score()

# Calculate industry expereince based candidate score
industry_exp_scores = calculate_score.industry_experience_score()

# Calculate others based candidate score
others_scores = calculate_score.others_score()

# Calculate techinical publications based candidate score
tech_publications_scores = calculate_score.technical_publications_score()

# Merge the four dataframes based on candidate_id column
merged_df = pd.merge(uni_ranking_scores, teaching_exp_scores, on="candidate_id")
merged_df = pd.merge(merged_df, industry_exp_scores, on="candidate_id")
merged_df = pd.merge(merged_df, others_scores, on="candidate_id")
merged_df = pd.merge(merged_df, tech_publications_scores, on="candidate_id")

# Create a total_score col in the merged_df
merged_df['total_score'] = merged_df['uni_ranking_score']+merged_df['teaching_exp_score']+\
                           merged_df['industry_exp_score']+merged_df['others_total']+\
                           merged_df['technical_publications_score']

# Save the results in a csv called output
merged_df.to_csv('output.csv', index=False)

# Upload results into 'score_cal_results' table of wire db
calculate_score.upload_cal_results()

# Print results in the terminal
print(merged_df)