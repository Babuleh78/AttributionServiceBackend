
from django.shortcuts import render, get_object_or_404, redirect


composerProfiles = [
    {
        "ID": 1,
        "Name": "Макс Рихтер",
        "AnalyzedWorks": 18,
        "AnalysisCost": 660,
        "TotalIntervals": 188190,
        "PortraitURL": "http://localhost:9000/images/richter-6x9.jpg",
        "Period": "2002 - настоящее время",
        "PolyphonyType": "Минималистичный контрапункт",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 32.7, "StdDev": 2.4},
            {"IntervalGroup": "Терции", "Frequency": 24.1, "StdDev": 1.9},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 18.3, "StdDev": 2.1},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 12.8, "StdDev": 1.7},
            {"IntervalGroup": "Октавы", "Frequency": 11.1, "StdDev": 1.5},
        ],
        "Biography": "Макс Рихтер — британский композитор-постминималист немецкого происхождения (род. 1966). Классически образованный выпускник Королевской академии музыки, он стал одним из самых влиятельных современных авторов, работая на стыке академической традиции и электронной музыки.",
    },
    {
        "ID": 2,
        "Name": "Людвиг Ван Бетховен",
        "AnalyzedWorks": 32,
        "AnalysisCost": 890,
        "TotalIntervals": 285430,
        "PortraitURL": "http://localhost:9000/images/bethoven.jpg",
        "Period": "1770-1827",
        "PolyphonyType": "Классика + контрапункт",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 28.4, "StdDev": 3.2},
            {"IntervalGroup": "Терции", "Frequency": 26.8, "StdDev": 2.8},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 22.1, "StdDev": 2.5},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 15.3, "StdDev": 2.1},
            {"IntervalGroup": "Октавы", "Frequency": 7.4, "StdDev": 1.8},
        ],
        "Biography": "Великий немецкий композитор, пианист и дирижёр. Последний представитель венской классической школы. ключевая фигура западной классической музыки в период между классицизмом и романтизмом.",
    },
    {
        "ID": 3,
        "Name": "Дзё Хисаиси",
        "AnalyzedWorks": 24,
        "AnalysisCost": 720,
        "TotalIntervals": 215670,
        "PortraitURL": "http://localhost:9000/images/dze.jpg",
        "Period": "1981 - настоящее время",
        "PolyphonyType": "Остинато",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 30.2, "StdDev": 2.1},
            {"IntervalGroup": "Терции", "Frequency": 25.6, "StdDev": 1.9},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 20.8, "StdDev": 2.0},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 14.7, "StdDev": 1.6},
            {"IntervalGroup": "Октавы", "Frequency": 8.7, "StdDev": 1.4},
        ],
        "Biography": "Японский композитор и музыкальный директор. Известен своими саундтреками к аниме-фильмам Хаяо Миядзаки. Сочетает элементы западной классической музыки с японскими традиционными мотивами.",
    },
    {
        "ID": 4,
        "Name": "Пьер Булез",
        "AnalyzedWorks": 16,
        "AnalysisCost": 580,
        "TotalIntervals": 172890,
        "PortraitURL": "http://localhost:9000/images/PierB.jpg",
        "Period": "1925-2016",
        "PolyphonyType": "Серийный контрапункт",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 35.8, "StdDev": 4.2},
            {"IntervalGroup": "Терции", "Frequency": 18.9, "StdDev": 3.1},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 16.4, "StdDev": 2.8},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 19.2, "StdDev": 3.0},
            {"IntervalGroup": "Октавы", "Frequency": 9.7, "StdDev": 2.1},
        ],
        "Biography": "Французский композитор, дирижёр и музыкальный теоретик. Один из лидеров послевоенного авангарда. Разработал технику сериализма и был пионером электронной музыки.",
    },
    {
        "ID": 5,
        "Name": "Дюк Эллингтон",
        "AnalyzedWorks": 28,
        "AnalysisCost": 820,
        "TotalIntervals": 245320,
        "PortraitURL": "http://localhost:9000/images/DuckE.jpg",
        "Period": "1899-1974",
        "PolyphonyType": "Джазовая гетерофония",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 27.6, "StdDev": 2.3},
            {"IntervalGroup": "Терции", "Frequency": 29.4, "StdDev": 2.1},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 19.8, "StdDev": 1.9},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 16.2, "StdDev": 1.7},
            {"IntervalGroup": "Октавы", "Frequency": 7.0, "StdDev": 1.2},
        ],
        "Biography": "Американский джазовый композитор, пианист и руководитель оркестра. Один из наиболее влиятельных фигур в истории джаза. Создал уникальный оркестровый звук и написал более 1000 произведений.",
    },
    {
        "ID": 6,
        "Name": "Филип Гласс",
        "AnalyzedWorks": 22,
        "AnalysisCost": 750,
        "TotalIntervals": 198560,
        "PortraitURL": "http://localhost:9000/images/PhilG.jpg",
        "Period": "1937 - настоящее время",
        "PolyphonyType": "Минималистичная гетерофония",
        "IntervalStats": [
            {"IntervalGroup": "Унисоны и секунды", "Frequency": 33.5, "StdDev": 1.8},
            {"IntervalGroup": "Терции", "Frequency": 22.3, "StdDev": 1.6},
            {"IntervalGroup": "Кварты и квинты", "Frequency": 21.7, "StdDev": 1.7},
            {"IntervalGroup": "Сексты и септимы", "Frequency": 13.9, "StdDev": 1.4},
            {"IntervalGroup": "Октавы", "Frequency": 8.6, "StdDev": 1.2},
        ],
        "Biography": "Американский композитор-минималист. Один из наиболее влиятельных композиторов конца XX - начала XXI века. Известен своими повторяющимися структурами и гипнотическими музыкальными паттернами.",
    },
]


def getComposerById(composer_id):
    for composer in composerProfiles:
        if composer["ID"] == composer_id:
            return composer
    return None


def getComposers():
    return composerProfiles


def searchComposers(pattern):
    if not pattern:
        return composerProfiles
    pattern = pattern.lower()
    return [c for c in composerProfiles if pattern in c["Name"].lower()]


def getAttributionCandidates():
    return composerProfiles[:3]


def get_composers_with_stats(request):
    search_pattern = request.GET.get('query', '')
    
    if search_pattern:
        composers = searchComposers(search_pattern)
    else:
        composers = getComposers()

    attribution_candidates = getAttributionCandidates()
    candidate_count = len(attribution_candidates)

    return render(request, 'main_page.html', {
        'composerProfiles': composers,
        'searchPattern': search_pattern,
        'candidateCount': candidate_count,
    })


def get_composer_interval_profile(request, id):
    composer = getComposerById(id)
    if not composer:
        from django.http import Http404
        raise Http404("Композитор не найден")
    
    return render(request, 'composer_profile.html', {
        'composer': composer,
    })


def view_attribution_results(request):
    attribution_candidates = getAttributionCandidates()

    candidates_with_prices = []
    total_sum = 0.0

    for candidate in attribution_candidates:
        calculated_price = float(candidate["AnalysisCost"]) * 300 / 60
        total_sum += calculated_price
        candidate_with_price = {**candidate, "CalculatedPrice": calculated_price}
        candidates_with_prices.append(candidate_with_price)

    return render(request, 'attribution_candidates.html', {
        'attributionCandidates': candidates_with_prices,
        'totalSum': total_sum,
    })


def add_to_cart(request):
    if request.method == "POST":
        composer_id = request.POST.get("composer_id")
        if "cart" not in request.session:
            request.session["cart"] = []
        request.session["cart"].append(composer_id)
        request.session.modified = True

    return redirect("main_page")