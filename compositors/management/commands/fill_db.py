from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from compositors.models import Composer, Analysis, ComposerAnalysis
from compositors.calc import calc
from django.utils import timezone
import random
from datetime import timedelta

def random_date():
    return timezone.now() - timedelta(days=random.randint(0, 365))

def random_timedelta():
    return timedelta(days=random.randint(1, 30))


composerProfiles = [
    {
        "ID": 1,
        "Name": "Макс Рихтер",
        "AnalyzedWorks": 18,
        "TotalIntervals": 188190,
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
        "TotalIntervals": 285430,
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
        "TotalIntervals": 215670,
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
        "TotalIntervals": 172890,
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
        "TotalIntervals": 245320,
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
]


def add_users():
    # Обычный пользователь
    if not User.objects.filter(username="user").exists():
        User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    
    # Суперпользователь 
    if not User.objects.filter(username="root").exists():
        User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    # Пользователь-создатель 
    if not User.objects.filter(username="creator").exists():
        User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password="1234",
            first_name="Creator",
            last_name="User",
            is_staff = True,
        )

    # Дополнительные пользователи
    for i in range(1, 10):
        if not User.objects.filter(username=f"user{i}").exists():
            User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        if not User.objects.filter(username=f"root{i}").exists():
            User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"root{i}", last_name=f"root{i}")

def add_composers():
    for composer_data in composerProfiles:
        if Composer.objects.filter(name=composer_data["Name"]).exists():
            continue

        Composer.objects.create(
            name=composer_data["Name"],
            biography=composer_data["Biography"], 
            analyzed_works=composer_data["AnalyzedWorks"],
            total_intervals=composer_data["TotalIntervals"],
            period=composer_data["Period"],
            polyphony_type=composer_data["PolyphonyType"],
            portrait_url=composer_data.get("PortraitURL"),  
            interval_stats=composer_data["IntervalStats"]
        )



def add_analysiss():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    composers = Composer.objects.all()

    if not users.exists() or not moderators.exists() or not composers.exists():
        print("Недостаточно данных для создания анализов")
        return

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_analysis(status, composers, owner, moderators)

    add_analysis(1, composers, users[0], moderators)
    add_analysis(2, composers, users[0], moderators)


def add_analysis(status, composers, owner, moderators):
    analysis = Analysis(status=status, owner=owner)

    if status in [3, 4]:
        analysis.moderator = random.choice(moderators)
        analysis.date_complete = random_date()
        analysis.date_formation = analysis.date_complete - random_timedelta()
        analysis.date_created = analysis.date_formation - random_timedelta()
    else:
        analysis.date_formation = random_date()
        analysis.date_created = analysis.date_formation - random_timedelta()

    analysis.save()

    selected_composers = random.sample(list(composers), min(3, len(composers)))
    for composer in selected_composers:
        anonymous_stats = []
        for group in composer.interval_stats:
            noise = random.uniform(-5.0, 5.0)
            freq = max(0.0, group["Frequency"] + noise)
            anonymous_stats.append({
                "IntervalGroup": group["IntervalGroup"],
                "Frequency": round(freq, 1)
            })

        coincidence = 0
        if analysis.status == 3:
            coincidence = calc(composer.interval_stats, anonymous_stats)

        ca = ComposerAnalysis(
            analysis=analysis,
            composer=composer,
            anonymous_interval_stats=anonymous_stats,
            potential_coincidence=int(coincidence)  
        )
        ca.save()

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        add_users()
        add_composers()
        add_analysiss()
        self.stdout.write(self.style.SUCCESS("База данных успешно заполнена!"))