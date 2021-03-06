import copy
try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()
import inspect
from datetime import date, timedelta, datetime
from django.utils.module_loading import import_string
import arrow
from . import conf

RESOLUTION_CHOICES = ['week', 'month', 'day']

class CohortAnalysis:
    # Initialize this class with a cohort queryset
    def __init__(self, resolution=None, end_date=None):
        if not resolution in RESOLUTION_CHOICES:
            resolution = RESOLUTION_CHOICES[0]
        self.resolution = resolution
        self.start_date = None
        self.end_date = arrow.get(end_date).datetime
        self.date_range() # init date range


    def date_range(self):
        if not self.end_date:
            end_date = arrow.now().replace(days=+1)
            self.end_date = end_date.floor('day').datetime
        if not self.start_date:
            replacement = {}
            replacement["%ss" % self.resolution] = -conf.COHORT_RANGE
            self.start_date = arrow.get(self.end_date).replace(**replacement).floor('day').datetime


    @property
    def date_range_set(self):
        '''Make a list of dates based on the resolution'''
        # Take the date_range and chop it up into weeks
        # get a list of dates in the week
        # add the list to the date_range_set

        date_list = []
        actual_start = arrow.get(self.start_date).floor(self.resolution)
        actual_end = arrow.get(self.end_date).ceil(self.resolution)
        iter_date = actual_start
        while iter_date < actual_end:
            period_ceil = arrow.get(iter_date).ceil(self.resolution)
            date_list.append([iter_date.datetime, period_ceil.datetime])
            replacement = {}
            replacement["%ss" % self.resolution] = +1
            iter_date = arrow.get(iter_date).replace(**replacement)
        return date_list


    def get_cohorts(self):
        '''Gets a list of querysets, "cohorts", of users.
        Subclass CohortAnalysis and overwrite get_cohorts to define your own.
        Must return a list of BaseCohort objects.

        Defaults to user signup week unless analysis_resolution is "month"'''

        range_field = '%s__range' % (conf.COHORT_DATE_JOINED_FIELD)
        user_filter = {}
        user_filter[range_field] = (self.start_date, self.end_date)

        user_list = User.objects.filter(**user_filter)

        if conf.COHORT_USER_FILTER:
            method = import_string(conf.COHORT_USER_FILTER)
            if method:
                user_list = method(user_list)
        cohorts = []
        for i in self.date_range_set:
            cohort = {}
            cohort_users = []
            for user in user_list:
                date_joined = getattr(user, conf.COHORT_DATE_JOINED_FIELD)
                if date_joined >= i[0] and date_joined <= i[1]:
                    cohort_users.append(user)
            cohort['start_date'] = i[0]
            cohort['users'] = cohort_users
            cohorts.append(cohort)
        return [BaseCohort(i, self.date_range_set) for i in cohorts]


    def methods(self, c):
        '''Gets all the methods from a given class'''
        return (m for m in (getattr(c, d) for d in dir(c))
                if inspect.ismethoddescriptor(m) or inspect.ismethod(m))


    @property
    def get_metrics(self):
        '''Gets a list of metrics functions to perform on the cohorts'''
        # TODO turn this into a list instead of a generator
        klass = import_string(conf.COHORT_ANALYSIS_METRICS)
        c = klass()
        metrics = self.methods(c)
        return metrics


    @property
    def get_metrics_choices(self):
        '''Returns a list of tuples for the function choices available
        used for the analysis page to select different metrics.
        Choices are named after the function name.
        '''
        choices = []
        for i in self.get_metrics:
            choices.append((i, i.__name__))
        return choices


    def get_metrics_function_by_choice(self, choice):
        for i in self.get_metrics_choices:
            metric_function = i[0]
            if i[1] == choice:
                return i[0]
        return metric_function


class BaseCohort:
    '''Subclass this to define a different metric'''
    # Initialize this class with a cohort queryset
    def __init__(self, cohort, date_range_set):
        self.name = cohort['start_date']
        self.cohort = cohort['users']
        self.date_range_set = date_range_set
        self.start_date = cohort['start_date']


    @property
    def date_set(self):
        # FIXME make sure that the last week doesn't get cut off
        revised_date_range_set = self.date_range_set
        revised_date_range_list = copy.deepcopy(revised_date_range_set)
        for i in revised_date_range_list:
            if i[0] < self.start_date:
                revised_date_range_set.remove(i)
        return revised_date_range_set


    def analyze(self, metric_choice=None):
        ''' Analyzes the cohorts based on the metric function defined.'''
        if metric_choice == None:
            metric = next(CohortAnalysis().get_metrics)
            metric_choice = metric.__name__
        else:
            metric = CohortAnalysis().get_metrics_function_by_choice(metric_choice)
        cohort_analysis = metric(self.cohort, self.date_set)
        analysis = {
            "metric_choice": metric_choice,
            "count": len(self.cohort),
            "analysis": cohort_analysis,
        }

        return analysis
