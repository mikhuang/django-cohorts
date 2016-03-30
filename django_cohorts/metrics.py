class CohortAnalysisMetrics:
    '''Create your analysis metrics here. Must return a list of floats.'''
    def logins(self, cohort, date_range_set):
        '''Get a percentage of users in the cohort that last logged in
        during the specified date range and chunk. Returns a list of floats.'''
        analysis = []
        for i in date_range_set:
            count = 0
            for user in cohort:
                if user.last_login and user.last_login >= i[0] and user.last_login <= i[1]:
                    count += 1
            try:
                percentage = (float(count)/float(len(cohort))) *100
            except ZeroDivisionError:
                percentage = float(0)
            analysis.append(percentage)
        return analysis
