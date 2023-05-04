# Project Name: Scoring Algorithm for Candidate Evaluation

## Overview
The Scoring Algorithm is a Python program that evaluates the qualifications of a candidate based on several predefined criteria. It uses a manual grading criteria to assign points to each criterion and generates a final score based on the total number of points awarded. This scoring system aims to provide an objective and comprehensive evaluation of each candidate's suitability for the position.

## Criteria
The Scoring Algorithm evaluates candidates based on the following criteria:

1. University of Graduation (Maximum 15 points):
The university of the candidate's last degree is evaluated based on its ranking. A PHD candidate having all the previous degrees including the PHD from a top 100 university will be awarded 15 points, while those from other universities will receive a deduction based on their QS or THES ranking. If a candidate does not have a PHD degree, the maximum score he can get is a 5 given both his BSC and Masters are from a top 100 university. A proportionate deduction from 5 points will be applied if any or both of these degrees are not from a top 100 university.

2. Teaching Experience (Maximum 15 points):
Candidates with teaching experience in non-Arabic-language universities will receive 3 points for each year of experience, with a maximum of 15 points. Candidates with teaching experience in Arabic-language universities will receive 2 points for each year of experience, with a maximum of 10 points.

3. Technical Publications (Research Experience) (Maximum 15 points):
Candidates will receive 2 points for each journal paper and 1 point for each conference paper, book chapter, or any other paper/book contribution. The journals should be from the last few years, SCOPUS indexed and be in the field the candidate is applying for. The algorithm takes in an academic reference as an input. It then uses an API to connect to GPT-4 to split the reference into its constituents i.e. article title, journal name, publication year, and DOI. Once the article name is parsed, it is then compared with an existing database of journals to get their SJR Quartile ranks using Fuzzy String matching.

4. Industrial Experience (Maximum 5 points):
Candidates will receive 1 point for each year of industry experience, with a maximum of 5 points.

5. Others (Maximum 10 points):
Candidates will receive 2 points for patents, 2 points for supervising graduation projects and theses, and 2 points for funded research projects. The algorithm uses a weighted method to assign scores for funded research. Maximum of 2 points will be given to a candidate who has received the maximum funds among all the applicants. All other candidates' scores for funded research are calculated relative to the top candidate. Candidates will receive 1 point each for committee work, working on quality assurance and academic accreditation, being head of a department or establishing a department, management and/or administrative activities, and certificates and professional training. Candidates management experience is considered from any of his teaching, work or industry experience. Candidates will receive 1 point for awards.

# Usage
The Scoring Algorithm can be used to evaluate the qualifications of candidates for a particular position. The user needs to input the candidate's details, including their academic references, teaching experience, industrial experience, technical publications, and other relevant information. The algorithm will then calculate the candidate's final score based on the predefined criteria.

# Conclusion
The Scoring Algorithm provides an objective and comprehensive evaluation of a candidate's qualifications based on various factors. It is designed to help employers make informed decisions while hiring candidates for a particular position. The algorithm can be customized and scaled to suit specific needs and requirements.