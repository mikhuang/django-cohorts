from django.template import RequestContext
from django.shortcuts import render_to_response
from django_cohorts.analysis import CohortAnalysis

def cohort_analysis(request):
    # if request.method == 'POST':
    #     form = CohortAnalysisForm(request.POST)
    #     if form.is_valid():
    #         pass# Do something to change the analysis shown
    resolution = request.GET.get('resolution')
    end_date = request.GET.get('end_date')
    analysis = CohortAnalysis(resolution, end_date)
    cohorts = analysis.get_cohorts()

    context = {
        "resolution": resolution,
        "metric_choice": request.GET.get('metric'),
        "analysis": analysis,
        "cohorts": cohorts,
    }
    return render_to_response('cohorts/cohort_analysis.html', context, context_instance=RequestContext(request))
