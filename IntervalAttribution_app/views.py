from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from IntervalAttribution_app.models import Composer, Analysis, ComposerAnalysis
from IntervalAttribution_app.calc import calc


def index(request):
    composer_name = request.GET.get("query", "")
    composers = Composer.objects.filter(status=1)

    if composer_name:
        composers = composers.filter(name__icontains=composer_name)

    context = {
        "composer_name": composer_name,
        "composers": composers
    }

    draft_analysis = get_draft_analysis()
    if draft_analysis:
        context["composers_count"] = len(draft_analysis.get_composers())
        context["draft_analysis"] = draft_analysis

    return render(request, "main_page.html", context)


def composer_page(request, composer_id):
    composer = Composer.objects.get(id=composer_id)

    if composer.status == 2:
         return render(request, "404.html")
    
    context = {
        "composer": Composer.objects.get(id=composer_id)
    }


    return render(request, "composer_profile.html", context)


def analysis_page(request, analysis_id):
    if not Analysis.objects.filter(pk=analysis_id).exists():
        return render(request, "404.html")

    analysis = Analysis.objects.get(id=analysis_id)
    
    if analysis.status == 5:
        return render(request, "404.html")

    total_sum = 0
    composers_with_cost = []  
    composers = analysis.get_composers() 

    for composer in composers:
        calculated_cost = int(calc(composer))
        total_sum += calculated_cost
        composer_with_cost = {**composer, 'calculated_cost': calculated_cost}
        composers_with_cost.append(composer_with_cost)

    context = {
        "analysis": analysis,
        "totalSum": total_sum,
        "composers": composers_with_cost,  
    }

    return render(request, "attribution_results.html", context)


def add_composer_to_draft_analysis(request, composer_id):
    composer_name = request.POST.get("composer_name")
    redirect_url = f"/?composer_name={composer_name}" if composer_name else "/composers"

    draft_analysis = get_draft_analysis()
    if draft_analysis is None:
        draft_analysis = Analysis.objects.create()
        draft_analysis.owner = get_current_user()
        draft_analysis.date_created = timezone.now()
        draft_analysis.save()

    composer = Composer.objects.get(pk=composer_id)
    if ComposerAnalysis.objects.filter(analysis=draft_analysis, composer=composer).exists():
        return redirect(redirect_url)

    item = ComposerAnalysis(
        analysis=draft_analysis,
        composer=composer
    )
    item.save()

    return redirect(redirect_url)


def delete_analysis(request, analysis_id):
    if not Analysis.objects.filter(pk=analysis_id).exists():
        return redirect("/composers")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE analysiss SET status=5 WHERE id = %s", [analysis_id])

    return redirect("/composers")


def get_draft_analysis():
    return Analysis.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()