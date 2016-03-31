from django.conf import settings

# field name for User model for when user joined
COHORT_DATE_JOINED_FIELD = getattr(settings, 'COHORT_DATE_JOINED_FIELD', 'date_joined')
COHORT_ANALYSIS_METRICS = getattr(settings, 'COHORT_ANALYSIS_METRICS', 'django_cohorts.metrics.CohortAnalysisMetrics')
COHORT_USER_FILTER = getattr(settings, 'COHORT_USER_FILTER', None)
COHORT_RANGE = getattr(settings, 'COHORT_RANGE', 9) # number of weeks, days, etc
