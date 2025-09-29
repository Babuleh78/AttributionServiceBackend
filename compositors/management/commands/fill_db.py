from django.core.management.base import BaseCommand
from compositors.utils import *
from compositors.models import *
import random


composerProfiles = [
    {
        "ID": 1,
        "Name": "Макс Рихтер",
        "AnalyzedWorks": 18,
        "AnalysisCost": 399,
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
        "AnalysisCost": 419,
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
        "AnalysisCost": 459,
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
        "AnalysisCost": 419,
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
        "AnalysisCost": 489,
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
        "AnalysisCost": 409,
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


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_composers():
    for composer_data in composerProfiles:
        Composer.objects.create(
            name=composer_data["Name"],
            description=composer_data["Biography"],
            price=composer_data["AnalysisCost"],
            analyzed_works=composer_data["AnalyzedWorks"],
            total_intervals=composer_data["TotalIntervals"],
            period=composer_data["Period"],
            polyphony_type=composer_data["PolyphonyType"],
            image=composer_data["PortraitURL"],
            interval_stats=composer_data["IntervalStats"]

        )


def add_analysiss():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    composers = Composer.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_analysis(status, composers, owner, moderators)

    add_analysis(1, composers, users[0], moderators)
    add_analysis(2, composers, users[0], moderators)


def add_analysis(status, composers, owner, moderators):
    analysis = Analysis.objects.create()
    analysis.status = status

    if status in [3, 4]:
        analysis.moderator = random.choice(moderators)
        analysis.date_complete = random_date()
        analysis.date_formation = analysis.date_complete - random_timedelta()
        analysis.date_created = analysis.date_formation - random_timedelta()
    else:
        analysis.date_formation = random_date()
        analysis.date_created = analysis.date_formation - random_timedelta()

    analysis.owner = owner

    for composer in random.sample(list(composers), 3):
        item = ComposerAnalysis(
            analysis=analysis,
            composer=composer,
            length=100 * random.randint(1, 6),
        )

        if analysis.status == 3:
            item.value = -1

        item.save()

    analysis.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_composers()
        add_analysiss()
        print("База данных успешно заполнена!")