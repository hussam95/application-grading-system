import pandas as pd
import mysql.connector
import datetime
import requests
import os
from fuzzywuzzy import fuzz

class DBConnector:
    """
    A class for connecting to a MySQL database and loading tables as pandas DataFrames.
    
    Attributes:
    ----------
    host : str
        The hostname of the MySQL server.
    username : str
        The username to use for authentication.
    password : str
        The password to use for authentication.
    database : str
        The name of the database to connect to.
    
    Methods:
    -------
    load_tables() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Connects to the MySQL database and loads the candidate, degree_bsc, degree_master, and degree_phd tables
        as pandas DataFrames. Returns a tuple containing the DataFrames.
    """
    
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        
    def load_tables(self):
        """
        Connects to the MySQL database and loads the candidate, degree_bsc, degree_master, and degree_phd tables
        as pandas DataFrames. Returns a tuple containing the DataFrames.
        
        Returns:
        -------
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
            A tuple containing the candidate, degree_bsc, degree_master, and degree_phd DataFrames.
        """
        # Connect to the database
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )
        
        # Load candidate table as pandas DataFrame
        candidate_df = pd.read_sql_query("SELECT * FROM candidate", cnx)
        
        # Load degree_bsc table as pandas DataFrame
        degree_bsc_df = pd.read_sql_query("SELECT * FROM degree_bsc", cnx)

        # Load degree_master table as pandas DataFrame
        degree_master_df = pd.read_sql_query("SELECT * FROM degree_master", cnx)

        # Load degree_phd table as pandas DataFrame
        degree_phd_df = pd.read_sql_query("SELECT * FROM dergee_phd", cnx)

        # Load teaching_exp table as pandas DataFrame
        teaching_exp_df = pd.read_sql_query("SELECT * FROM teaching_exp", cnx)

        # Load industry_exp table as pandas DataFrame
        industry_exp_df = pd.read_sql_query("SELECT * FROM industry_exp", cnx)
        
        # Load patent_exp table as pandas DataFrame
        patents_df = pd.read_sql_query("SELECT * FROM patents", cnx) 
        
        # Load supervision_bsc table as pandas DataFrame
        supervision_bsc_df = pd.read_sql_query("SELECT * FROM supervision_bsc", cnx) 
        
        # Load supervision_masters table as pandas DataFrame
        supervision_masters_df = pd.read_sql_query("SELECT * FROM supervision_master", cnx) 
        
        # Load supervision_phd table as pandas DataFrame
        supervision_phd_df = pd.read_sql_query("SELECT * FROM supervision_phd", cnx) 
        
        # Load committee_work table as pandas DataFrame
        committee_work_df = pd.read_sql_query("SELECT * FROM committee_work", cnx) 
        
        # Load quality_accreditation table as pandas DataFrame
        quality_accreditation_df = pd.read_sql_query("SELECT * FROM quality_accreditation", cnx) 
        
        # Load certificates table as pandas DataFrame
        certificates_df = pd.read_sql_query("SELECT * FROM certificates", cnx) 
        
        # Load awards table as pandas DataFrame
        awards_df = pd.read_sql_query("SELECT * FROM awards", cnx) 
        
        # Load funded_research table as pandas DataFrame
        funded_research_df = pd.read_sql_query("SELECT * FROM funded_research", cnx) 
        
        # Load citation table as pandas DataFrame
        citation_df = pd.read_sql_query("SELECT * FROM citation", cnx) 
        # Close the connection
        cnx.close()
        
        # Return the DataFrames
        return candidate_df, degree_bsc_df, degree_master_df, degree_phd_df, teaching_exp_df, industry_exp_df, patents_df, supervision_bsc_df, supervision_masters_df, supervision_phd_df, committee_work_df, quality_accreditation_df, certificates_df, awards_df, funded_research_df, citation_df

class ScoreCalculator(DBConnector):
    """
    Class to assign a numerical score to a candidates application based on 5 major areas of past
    performance i.e. university rankings from which the candidate studied, teaching exp, industry exp,
    technical publications, and other variables such as patents, funded research, and committee work etc.
    
    Attributes:
    -----------
    host: str
        String containing the name of the server hosting the instance of MySQL db
    username: str
        String containing the username of a user added to the database
    password: str
        String containing the password of a user added to the database
    database: str
        String containing the name of the MySQL database
    candidate_df : pandas.DataFrame
        DataFrame containing candidate information including candidate_id
    degree_bsc_df : pandas.DataFrame
        DataFrame containing Bachelor's degree information including QS_uni_rank_bsc
    degree_master_df : pandas.DataFrame
        DataFrame containing Master's degree information including QS_uni_rank_master
    degree_phd_df : pandas.DataFrame
        DataFrame containing PhD degree information including QS_uni_rank_phd
    teaching_exp_df: pandas.DataFrame
        DataFrame containing teaching expreience information
    teaching_exp_df: pandas.DataFrame
        DataFrame containing teaching expreience information
    inudstry_exp_df: pandas.DataFrame
        DataFrame containing industry expreience information
    patents_df: pandas.DataFrame
        DataFrame containing patents information
    supervision_bsc_df: pandas.DataFrame
        DataFrame containing bsc supervision expreience information
    supervision_masters_df: pandas.DataFrame
        DataFrame containing masters supervision expreience information
    supervision_phd_df: pandas.DataFrame
        DataFrame containing phd supervision expreience information
    committee_work_df: pandas.DataFrame
        DataFrame containing committee work expreience information
    quality_accreditation_df: pandas.DataFrame
        DataFrame containing QA expreience information
    certificates_df: pandas.DataFrame
        DataFrame containing certificates information
    awards_df: pandas.DataFrame
        DataFrame containing awards information
    funded_research_df: pandas.DataFrame
        DataFrame containing funded research information
    citation_df: pandas.DataFrame
        DataFrame containing  technical publications information 
    """
    # University ranking vars
    MAX_SCORE_WITH_PHD_QS_LT_100 = 15
    MAX_SCORE_WITH_PHD_QS_GT_100 = 11.5
    NO_PHD_MAX_SCORE = 5
    DEDUCTION = 5

    # Teaching exp vars
    MAX_SCORE_NON_ARABIC_PER_YEAR = 3
    MAX_SCORE_ARABIC_PER_YEAR = 2  

    # Industry exp vars
    MAX_IND_EXP_SCORE_PER_YEAR = 1

    def __init__(self, host,username,password,database, candidate_df, degree_bsc_df, degree_master_df, degree_phd_df, teaching_exp_df, industry_exp_df, patents_df, supervision_bsc_df, supervision_masters_df, supervision_phd_df, committee_work_df, quality_accreditation_df, certificates_df, awards_df, funded_research_df, citation_df):
        super().__init__(host, username, password, database) # inherit host, username, pass, and db parameters from DBConnector class
        self.candidate_df = candidate_df
        self.degree_bsc_df = degree_bsc_df
        self.degree_master_df = degree_master_df
        self.degree_phd_df = degree_phd_df
        self.teaching_exp_df = teaching_exp_df
        self.industry_exp_df = industry_exp_df
        self.patents_df = patents_df
        self.supervision_bsc_df = supervision_bsc_df
        self.supervision_masters_df = supervision_masters_df
        self.supervision_phd_df = supervision_phd_df
        self.committee_work_df = committee_work_df
        self.quality_accreditation_df = quality_accreditation_df
        self.certificates_df = certificates_df
        self.awards_df = awards_df
        self.funded_research_df = funded_research_df
        self.citation_df = citation_df
        self.journal_ranks = pd.read_csv('journal_ranks.csv')


    def university_score(self):
        """
        Calculates the score for a candidate based on the ranking of the universities
        from which the candidate got different degrees from
        
        Returns:
        --------
        pandas.DataFrame
            df containing the university of graduation score for each candidate
        """
        scores = {}
        for candidate_id in self.candidate_df['candidate_id']:
            # Has PHD
            if candidate_id in self.degree_phd_df['candidate_id'].to_list():
                # Case 1: Phd degree qs <100 and bsc, masters <100
                if self.degree_phd_df.loc[self.degree_phd_df['candidate_id']==candidate_id, 'QS_uni_rank_phd'].iloc[0] <= 100:
                    if (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] <= 100) and \
                       (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] <= 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100
                        continue
                    # Case 2: phd <100 and master > 100, bsc <100
                    elif (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100) and \
                        (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100 - self.DEDUCTION
                        continue
                    # Case 3: phd <100 and bsc >100, masters <100
                    elif self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100 and \
                        (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100 - self.DEDUCTION
                        continue
                    # Case 4: phd <100 and master < 100 , bsc >100
                    elif (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100) and \
                        (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100 - self.DEDUCTION
                        continue
                    # Case 5: phd <100 and bsc <100 , masters >100
                    elif self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100 and \
                        (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100 - self.DEDUCTION
                        continue
                    # Case 6: Phd degree qs < 100 and bsc, masters >100 
                    else:
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_LT_100 - self.DEDUCTION*1.2
                        continue
                # Case 7: phd degree qs>100 and masters bsc <100
                else:
                    if (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] <= 100) and \
                       (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] <= 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100
                        continue
                    # Case 8: phd degree qs > 100 and master > 100 , bsc <100
                    elif (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100) and \
                        (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100 - self.DEDUCTION
                        continue
                    # Case 9: phd degree qs > 100 and bsc > 100 , master <100
                    elif self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100 and \
                        (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100 - self.DEDUCTION
                        continue

                    # Case 10: phd degree qs > 100 and master < 100 , bsc >100
                    elif (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100) and \
                        (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100 - self.DEDUCTION
                        continue
                    # Case 11: phd degree qs > 100 and bsc < 100 , master >100
                    elif self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100 and \
                        (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100):
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100 - self.DEDUCTION
                        continue

                    # Case 12: phd degree qs > 100 and bsc, masters > 100 
                    else:
                        scores[candidate_id] = self.MAX_SCORE_WITH_PHD_QS_GT_100 - 2*self.DEDUCTION/2
                        continue
            # No PHD
            else:
                # No Masters
                if (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id].empty):
                    # Case 13: no masters and bsc <100
                    if (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE -self.DEDUCTION/2
                    # Case 14: no masters and bsc >100
                    elif (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100):
                        scores[candidate_id] = self.DEDUCTION/3
                
                # No PHD has Masters
                else:
                    # Case 15: both masters and bsc qs <100
                    if (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100) and (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE
                        continue
                    # Case 16: bsc qs <100 , masters >100
                    elif (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100) and (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE - self.DEDUCTION/3.5
                        continue
                    # Case 17: master qs <100 , bsc >100
                    elif (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100) and (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE -self.DEDUCTION/3.5

                    # Case 16: bsc qs >100, masters <100 
                    elif (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] > 100) and (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] < 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE - self.DEDUCTION/3.5
                        continue
                    # Case 17: master qs >100, bsc <100 
                    elif (self.degree_bsc_df.loc[self.degree_bsc_df['candidate_id']==candidate_id, 'QS_uni_rank_bsc'].iloc[0] < 100) and (self.degree_master_df.loc[self.degree_master_df['candidate_id']==candidate_id, 'QS_uni_rank_master'].iloc[0] > 100):
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE -self.DEDUCTION/3.5
                    
                    # Case 18: both masters and bsc qs>100
                    else:
                        scores[candidate_id] = self.NO_PHD_MAX_SCORE - self.DEDUCTION/2


        return pd.DataFrame(scores.items(), columns=['candidate_id', 'uni_ranking_score'])
    
    def teaching_expereince_score(self):
        """
        Calculates the teaching experience score for each candidate in the candidate dataframe.

        Returns:
        A pandas dataframe containing the candidate IDs and their corresponding teaching experience scores.
        """

        # Create a list of Arab countries
        arabic_speaking_countries = ["Algeria", "Bahrain", "Comoros", "Djibouti", "Egypt", "Iraq", "Jordan", "Kuwait", "Lebanon", "Libya", "Mauritania", "Morocco", "Oman", "Palestine", "Qatar", "Saudi Arabia", "Somalia", "Sudan", "Syria", "Tunisia", "United Arab Emirates", "Yemen"]
        scores = {}
        for candidate_id in self.candidate_df['candidate_id']:
            # Filter teaching_exp_df for each candidate
            candidate_teaching_exp = self.teaching_exp_df[self.teaching_exp_df['candidate_id']==candidate_id]
            candidate_score = 0
            for _, row in candidate_teaching_exp.iterrows():
                # Convert the date strings to datetime objects
                if row['teaching_current_position'] == 'yes':
                    end_date = datetime.date.today()
                else:
                    end_date = pd.to_datetime(row['teaching_to_end_date']).date()


                start_date = pd.to_datetime(row['teaching_from_start_date']).date()
                
                
                # Calculate the duration in years and append to the durations list
                duration_years = (end_date - start_date).days/365.25
                
                # Cap duration to a maximum of 5 years
                if duration_years >5:
                    duration_years = 5
                else:
                    duration_years = duration_years
                
                teaching_exp_country = row['teachingexp_country']

                if teaching_exp_country.lower() in [arab_country.lower() for arab_country in arabic_speaking_countries]:
                    current_score = self.MAX_SCORE_ARABIC_PER_YEAR*duration_years
                    candidate_score += current_score
                else:
                    current_score = self.MAX_SCORE_NON_ARABIC_PER_YEAR * duration_years
                    candidate_score += current_score
            
            # Cap overall maximum teaching score to 15    
            if candidate_score > 15.0:
                scores[candidate_id] = 15
            else:
                scores[candidate_id] = candidate_score

        return  pd.DataFrame(scores.items(), columns=['candidate_id', 'teaching_exp_score'])

    def industry_experience_score(self):
        """
        Computes the industry experience score for each candidate in the candidate dataframe.
        
        Returns:
        - pandas DataFrame: a dataframe with two columns: 'candidate_id' and 'industry_exp_score'.
        """

        scores = {}
        for candidate_id in self.candidate_df['candidate_id']:
            # Filter industry_exp_df for each candidate
            candidate_ind_exp = self.industry_exp_df[self.industry_exp_df['candidate_id']==candidate_id]
            candidate_score = 0
            for _, row in candidate_ind_exp.iterrows():
                # Convert the date strings to datetime objects
                if row['industry_current_position'] == 'yes':
                    end_date = datetime.date.today()
                else:
                    end_date = pd.to_datetime(row['industry_to_end_date']).date()


                start_date = pd.to_datetime(row['industry_from_start_date']).date()
                
                
                # Calculate the duration in years 
                duration_years = (end_date - start_date).days/365.25
                
                # Cap duration to a maximum of 5 years
                if duration_years >5:
                    duration_years = 5
                else:
                    duration_years = duration_years
                
                
                current_score = self.MAX_IND_EXP_SCORE_PER_YEAR*duration_years
                candidate_score += current_score
                
            
            # Cap overall maximum industry score to 5    
            if candidate_score > 5.0:
                scores[candidate_id] = 5
            else:
                scores[candidate_id] = candidate_score
         
        return  pd.DataFrame(scores.items(), columns=['candidate_id', 'industry_exp_score'])

    def others_score(self):
        """
        Calculate the "Others" score for each candidate based on their patents, supervision,
        committee work, quality accreditation, certificates, awards, management experience,
        and funded research.

        Returns:
        --------
        A pandas DataFrame containing the "Others" score for each candidate and the scores for each component (patents, supervision, committee work, quality accreditation, certificates, awards, management experience, and funded research).

        """
        patents_scores = {}
        supervision_scores = {}
        committee_work_scores = {}
        quality_accreditation_scores = {}
        certificates_scores = {}
        awards_scores = {}
        funded_research_scores = {}
        management_exp_scores = {}
        funded_research_total_per_candidate = {}
        scores = {}
        for candidate_id in self.candidate_df['candidate_id'].unique().tolist():
            # Patents
            if candidate_id in self.patents_df['candidate_id']:
                patents_scores[candidate_id] = 2
            else:
                patents_scores[candidate_id] = 0
            
            # Supervision
            if candidate_id in self.supervision_bsc_df['candidate_id'].unique().tolist() or self.supervision_masters_df['candidate_id'].unique().tolist() or self.supervision_phd_df['candidate_id'].unique().tolist():
                supervision_scores[candidate_id] = 2
            else:
                supervision_scores[candidate_id] = 0

            # Comittee Work
            if candidate_id in self.committee_work_df['candidate_id'].unique().tolist():
                committee_work_scores[candidate_id] = 1 
            else:
                committee_work_scores[candidate_id] = 0

            # Quality Accreditation
            if candidate_id in self.quality_accreditation_df['candidate_id'].unique().tolist():
                quality_accreditation_scores[candidate_id] = 1
            else:
                quality_accreditation_scores[candidate_id] = 0
            
            # Certificates
            if candidate_id in self.certificates_df['candidate_id'].unique().tolist():
                certificates_scores[candidate_id] = 1
            else:
                certificates_scores[candidate_id] = 0

            # Awards
            if candidate_id in self.awards_df['candidate_id'].unique().tolist():
                awards_scores[candidate_id] = 1
            else:
                awards_scores[candidate_id] = 0

            # Management Exp
            if 'yes' in self.teaching_exp_df[self.teaching_exp_df['candidate_id']==candidate_id]['teaching_administrative_position'].tolist() or 'yes' in self.industry_exp_df[self.industry_exp_df['candidate_id']==candidate_id]['industry_administritive_position'].tolist():
                management_exp_scores[candidate_id] = 1
            else:
                management_exp_scores[candidate_id] = 0

            # Funded Research 
            funded_total_amount = self.funded_research_df[self.funded_research_df['candidate_id']==candidate_id]['funded_amount_usd'].sum()
            funded_research_total_per_candidate[candidate_id] = funded_total_amount
        
        max_funded_amount = max(funded_research_total_per_candidate.values())
        for candidate_id in self.candidate_df['candidate_id'].unique().tolist():
            candidate_funded_amount = self.funded_research_df[self.funded_research_df['candidate_id']==candidate_id]['funded_amount_usd'].sum()
            if max_funded_amount !=0:
                funded_research_scores[candidate_id] = (candidate_funded_amount/max_funded_amount)*2
            
            # Real time entries; funded research amt can be zero for few; avoid error in that case
            else:
                funded_research_scores[candidate_id] = 0
                
        scores = {"patent_others":patents_scores, "supervision_others":supervision_scores,
                  "committe_others":committee_work_scores,"qa_others": quality_accreditation_scores,
                  "certificates_others":certificates_scores,"awards_others":awards_scores,
                  "managemnet_exp_others":management_exp_scores,"funded_research_others":funded_research_scores}
        
        # create the others output dataframe
        df = pd.DataFrame(scores)

        # Sum components of others to get others_total
        df['others_total'] = df.sum(axis=1)

        # Add candidate_id col
        df['candidate_id'] = self.candidate_df['candidate_id'].unique()
        
        return pd.DataFrame(df)
    
    
    def __journal_name_parser(self, technical_publication) -> str:
        """
        Extracts the name of the journal from a technical publication.

        Parameters:
            technical_publication (str): The text of the technical publication.

        Returns:
            str: The name of the journal if found, or an empty string if not.

        Raises:
            Exception: If an error occurs while processing the API request or parsing the response.
        """
        # Define the input data for the API request
        data = {
            "input": {
                "text": technical_publication
               }
        }
        # Add authorization headers for the Scale API
        headers = {"Authorization": "Basic clgjomk4t09l71axugxxzgmzq"}

        try:
            # Make a POST request to the Scale API
            response = requests.post(
                "https://dashboard.scale.com/spellbook/api/v2/deploy/9e63bii",
                json=data,
                headers=headers
            )

            # Extract the output JSON from the response and convert it to a Python dictionary
            json_out = eval(response.json()['output'])

            # Loop through the dictionary to find the journal name and return it if found
            labels = ['title: ', 'journal: ', 'year: ', 'doi: ']
            for label, item in zip(labels, json_out):
                if label == 'journal: ':
                    return json_out
                

        # Catch any exceptions that occur during the API request or parsing and raise a new exception with a more informative message
        except Exception as e:
            raise Exception("Error occurred while processing the API request or parsing the response.") from e
    
    
    def __find_best_match(self,string1, df, column_name='Title', method='token_sort_ratio'):
        """
        Finds the best match for a given string in a pandas dataframe using fuzzy string matching.
        
        Parameters:
        -----------
        string1 : str
            The input string to find a match for.
        df : pandas DataFrame
            The dataframe containing the strings to match against.
        column_name : str, optional (default='Product Description')
            The name of the column in the dataframe containing the strings to match against.
        method : str, optional (default='token_sort_ratio')
            The fuzzy matching algorithm to use. Options include:
            - 'ratio': simple ratio
            - 'partial_ratio': partial ratio
            - 'token_sort_ratio': token sort ratio
            - 'token_set_ratio': token set ratio
            
        Returns:
        --------
        best_match : str
            The best matching string in the dataframe.
        max_similarity_score : float
            The similarity score between the input string and the best matching string.
        """
        # initialize variables
        best_match = None
        max_similarity_score = float('-inf')
        
        # iterate over dataframe rows and compute similarity scores
        for _, row in df.iterrows():
            string2 = row[column_name]
            similarity_score = getattr(fuzz, method)(string1, string2)
            
            # update best match if current similarity score is higher
            if similarity_score > max_similarity_score:
                max_similarity_score = similarity_score
                best_match = string2
                
        return best_match, max_similarity_score

    def __insert_values(self, values):
        """
        Insert values into the citation table for a given candidate ID and citation ID.

        Args:
            values (list): A list of values to be inserted into the citation table. The order of values should be as follows:
                        [cit_id, candidate_id, cit_research_title, cit_journal_title, cit_year_publication_issue_volume, cit_doi]

        Returns:
            None

        Raises:
            None
        """
        
        # create a connection to the database
        cnx = mysql.connector.connect(user=self.username, password=self.password, host=self.host, database=self.database)
        
        # Define the query with placeholders for the values to insert/update
        query = "INSERT INTO citation (cit_peer_reviewed_journals, cit_research_title, cit_journal_title, cit_year_publication_issue_volume, cit_doi, candidate_id, cit_id) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE cit_peer_reviewed_journals = VALUES(cit_peer_reviewed_journals), cit_research_title = VALUES(cit_research_title), cit_journal_title = VALUES(cit_journal_title), cit_year_publication_issue_volume = VALUES(cit_year_publication_issue_volume), cit_doi = VALUES(cit_doi)"
        # execute the query with the values
        cursor = cnx.cursor()
        cursor.execute(query, (values[6],values[2], values[3], values[4], values[5], values[1], values[0]))
        
        # commit the changes to the database
        cnx.commit()
        
        # close the cursor and connection
        cursor.close()


        # close the database connection
        cnx.close()

                    
    def technical_publications_score(self):
        """
        Calculate technical publications score for each candidate based on the citation data in the
        `citation_df` dataframe.
        The score is calculated based on the candidate's published journals and their SJR Quartile rank,
        where a higher SJR Quartile rank contributes more to the score. The maximum score is capped at 15.

        Returns:
        pandas.DataFrame: A dataframe containing the technical publications score for each candidate in the
        `candidate_df` dataframe. The dataframe has two columns: 'candidate_id' and
        'technical_publications_score'.

        """
        scores = {}
        cit_id = 1 
        for candidate_id in self.citation_df['candidate_id']:
            # Get publications for each candidate
            candidate_tech_publications = self.citation_df[self.citation_df['candidate_id']==candidate_id]['cit_peer_reviewed_journals'].values[0]
            
            # Run academic references through parser to fetch journal name
            publication_data_list = self.__journal_name_parser(candidate_tech_publications)
                
            candidate_score = 0  
             
            # Loop over the publication data list to get all parased publications
            for publication in zip(*[iter(publication_data_list)]*4):
                # Tuple to list
                publication = list(publication)
                # Add cit_id, candidate_id, and user input to the payload
                publication =[cit_id,candidate_id]+publication+[candidate_tech_publications]
                
                
                # Upload parsed data to citations table
                self.__insert_values(publication)
                cit_id+=1
                journal_name = publication[3]
                # Run through fuzzy_string method to find best match jorunal in journal dataset
                best_match_journal, max_similarity_score = self.__find_best_match(journal_name,self.journal_ranks,'Title')
                
                # Match is strong i.e. the journal candidate published in is a valid jorunal
                if max_similarity_score > 80:
                    sjr_quartile_rank = self.journal_ranks[self.journal_ranks['Title']==best_match_journal]['SJR Quartile']
                    if sjr_quartile_rank.values[0] == 'Q1':
                        candidate_score+=3
                        
                    elif sjr_quartile_rank.values[0] == 'Q2':
                        candidate_score+=2
                        
                    elif sjr_quartile_rank.values[0] == 'Q3':
                        candidate_score+=1

                    elif sjr_quartile_rank.values[0] == 'Q4' or sjr_quartile_rank.values[0] == '-':
                        candidate_score+=0.5
                    
                    else:
                        candidate_score+=0
            
                # Match is weak i.e. the journal candidate published in is not a valid journal
                else:
                    candidate_score+=0
            
            # Cap overall maximum industry score to 5    
            if candidate_score > 15.0:
                scores[candidate_id] = 15.0
            else:
                scores[candidate_id] = candidate_score
         
        return  pd.DataFrame(scores.items(), columns=['candidate_id', 'technical_publications_score'])
    
    def upload_cal_results(self):
        """
        Uploads a CSV file containing score calculation results to a MySQL table.

        Args:
            None.

        Returns:
            None.
        """
        # MySQL database connection
        mydb = mysql.connector.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )

        # Path to CSV file
        csv_file = 'output.csv'

        # Read CSV file into a pandas dataframe
        df = pd.read_csv(csv_file)

        # Check if the table already exists
        cursor = mydb.cursor()
        cursor.execute("SHOW TABLES LIKE 'score_cal_results'")
        result = cursor.fetchone()

        if result:
            # Table already exists, insert only new data
            existing_ids = set(pd.read_sql_query("SELECT candidate_id FROM score_cal_results", mydb)['candidate_id'])
            new_data = df[~df['candidate_id'].isin(existing_ids)]
            for row in new_data.itertuples():
                query = f"INSERT INTO score_cal_results ({', '.join(df.columns)}) VALUES {tuple(row[1:])}"
                cursor.execute(query)
        else:
            # Create a new table using the column names from the CSV file
            cols = ", ".join([f"{col} FLOAT" for col in df.columns])
            cursor.execute(f"CREATE TABLE score_cal_results ({cols})")

            # Insert all data from the CSV file into the new table
            for row in df.itertuples():
                query = f"INSERT INTO score_cal_results ({', '.join(df.columns)}) VALUES {tuple(row[1:])}"
                cursor.execute(query)

        # Commit changes and close database connection
        mydb.commit()
        mydb.close()
