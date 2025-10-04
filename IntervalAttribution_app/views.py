from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone
import random

from IntervalAttribution_app.models import Composer, Analysis, ComposerAnalysis
from IntervalAttribution_app.calc import calc

ANONYMOUS_WORK_STATS = [
    {"IntervalGroup": "Унисоны и секунды", "Frequency": 30.0},
    {"IntervalGroup": "Терции", "Frequency": 5.0},
    {"IntervalGroup": "Кварты и квинты", "Frequency": 20.0},
    {"IntervalGroup": "Сексты и септимы", "Frequency": 35.0},
    {"IntervalGroup": "Октавы", "Frequency": 10.0},
]

def get_composer_interval_stats(composer):
    """Возвращает статистику интервалов композитора с частотой и СКО"""
    return [
        {
            "IntervalGroup": "Унисоны и секунды",
            "Frequency": float(composer.unisons_seconds_freq or 0),
            "StdDev": float(composer.unisons_seconds_stddev or 0)
        },
        {
            "IntervalGroup": "Терции",
            "Frequency": float(composer.thirds_freq or 0),
            "StdDev": float(composer.thirds_stddev or 0)
        },
        {
            "IntervalGroup": "Кварты и квинты",
            "Frequency": float(composer.fourths_fifths_freq or 0),
            "StdDev": float(composer.fourths_fifths_stddev or 0)
        },
        {
            "IntervalGroup": "Сексты и септимы",
            "Frequency": float(composer.sixths_sevenths_freq or 0),
            "StdDev": float(composer.sixths_sevenths_stddev or 0)
        },
        {
            "IntervalGroup": "Октавы",
            "Frequency": float(composer.octaves_freq or 0),
            "StdDev": float(composer.octaves_stddev or 0)
        },
    ]


def get_anonymous_interval_stats(composer_analysis):
    """Возвращает анонимную статистику с частотой и СКО"""
    return [
        {
            "IntervalGroup": "Унисоны и секунды",
            "Frequency": float(composer_analysis.anon_unisons_seconds_freq or 0),
            "StdDev": float(composer_analysis.anon_unisons_seconds_stddev or 0)
        },
        {
            "IntervalGroup": "Терции",
            "Frequency": float(composer_analysis.anon_thirds_freq or 0),
            "StdDev": float(composer_analysis.anon_thirds_stddev or 0)
        },
        {
            "IntervalGroup": "Кварты и квинты",
            "Frequency": float(composer_analysis.anon_fourths_fifths_freq or 0),
            "StdDev": float(composer_analysis.anon_fourths_fifths_stddev or 0)
        },
        {
            "IntervalGroup": "Сексты и септимы",
            "Frequency": float(composer_analysis.anon_sixths_sevenths_freq or 0),
            "StdDev": float(composer_analysis.anon_sixths_sevenths_stddev or 0)
        },
        {
            "IntervalGroup": "Октавы",
            "Frequency": float(composer_analysis.anon_octaves_freq or 0),
            "StdDev": float(composer_analysis.anon_octaves_stddev or 0)
        },
    ]

def index(request):
    composer_name = request.GET.get("composerName", "")
    composers = Composer.objects.filter(status=1)

    

    if composer_name:
        composers = composers.filter(name__icontains=composer_name)

    context = {
        "composer_name": composer_name,
        "composerProfiles": composers
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
        "composer": Composer.objects.get(id=composer_id),
        "interval_stats": get_composer_interval_stats(composer)
    }


    return render(request, "composer_profile.html", context)


def analysis_page(request, analysis_id):
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
    except Analysis.DoesNotExist:
        return render(request, "404.html", status=404)

    if analysis.status == 5:  
        return render(request, "404.html", status=404)

    composer_analysis_items = ComposerAnalysis.objects.filter(analysis=analysis).select_related('composer')

    composers_with_cost = []

    for item in composer_analysis_items:
        composer = item.composer

        # Получаем статистику композитора и анонима
        composer_stats = get_composer_interval_stats(composer)
        anonymous_stats = get_anonymous_interval_stats(item)

        # Расчёт совпадения (если нужно — можно включить)
        # match_percentage = calc(composer_stats, anonymous_stats)
        # item.potential_coincidence = round(match_percentage, 2)
        # item.save(update_fields=['potential_coincidence'])

        match_percentage = item.potential_coincidence  # берём из БД

        composer_data = {
            'name': composer.name,
            'portrait_url': composer.portrait_url,
            'period': composer.period,
            'analyzed_works': composer.analyzed_works,
            'total_intervals': composer.total_intervals,
            'interval_stats': composer_stats,  # ← теперь это список, а не JSON
            'MatchPercent': match_percentage,
        }
        composers_with_cost.append(composer_data)

    context = {
        "analysis": analysis,
        "composers": composers_with_cost,
        "anonymousStats": get_anonymous_interval_stats(composer_analysis_items.first()) if composer_analysis_items else ANONYMOUS_WORK_STATS,
    }

    return render(request, "attribution_results.html", context)

def add_composer_to_draft_analysis(request, composer_id):
    composer_name = request.POST.get("composer_name")
    redirect_url = f"/?composer_name={composer_name}" if composer_name else "/composers"

    draft_analysis = get_draft_analysis()
    if draft_analysis is None:
        draft_analysis = Analysis.objects.create(
            owner=get_current_user(),
            date_created=timezone.now(),
            status=1
        )

    composer = Composer.objects.get(pk=composer_id)
    if ComposerAnalysis.objects.filter(analysis=draft_analysis, composer=composer).exists():
        return redirect(redirect_url)

    anon_stats = ANONYMOUS_WORK_STATS 

    # Создаём объект с заполнением полей
    item = ComposerAnalysis(
        analysis=draft_analysis,
        composer=composer,
        potential_coincidence=random.randint(80, 100),
        # Заполняем анонимные поля
        anon_unisons_seconds_freq=next(g["Frequency"] for g in anon_stats if g["IntervalGroup"] == "Унисоны и секунды"),
        anon_thirds_freq=next(g["Frequency"] for g in anon_stats if g["IntervalGroup"] == "Терции"),
        anon_fourths_fifths_freq=next(g["Frequency"] for g in anon_stats if g["IntervalGroup"] == "Кварты и квинты"),
        anon_sixths_sevenths_freq=next(g["Frequency"] for g in anon_stats if g["IntervalGroup"] == "Сексты и септимы"),
        anon_octaves_freq=next(g["Frequency"] for g in anon_stats if g["IntervalGroup"] == "Октавы"),
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