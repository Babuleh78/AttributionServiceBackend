package repository

import (
	"fmt"
	"strings"
)

type IntervalRepository struct {
}

func NewIntervalRepository() (*IntervalRepository, error) {
	return &IntervalRepository{}, nil
}

type ComposerProfile struct {
	ID             int            // Уникальный идентификатор композитора в системе
	Name           string         // Полное имя композитора
	AnalyzedWorks  int            // Количество проанализированных произведений композитора
	AnalysisCost   int            // Стоимость анализа одного произведения (в условных единицах)
	TotalIntervals int            // Общее количество проанализированных музыкальных интервалов
	PortraitURL    string         // URL-адрес портрета композитора
	Period         string         // Период творческой активности (годы жизни или творчества)
	IntervalStats  []IntervalStat // Статистика использования различных интервалов композитором
	Biography      string         // Краткая биографическая справка о композиторе
	PolyphonyType  string         // Тип полифонии
}

type IntervalStat struct {
	IntervalGroup string  // Группа интервалов (например: "Унисоны и секунды", "Терции")
	Frequency     float64 // Частотность использования данной группы интервалов в процентах
	StdDev        float64 // Стандартное отклонение частотности (показатель вариативности)
}

func (r *IntervalRepository) GetComposersWithIntervalStats() ([]ComposerProfile, error) {
	composerProfiles := []ComposerProfile{
		{
			ID:             1,
			Name:           "Макс Рихтер",
			AnalyzedWorks:  18,
			AnalysisCost:   660,
			TotalIntervals: 188190,
			PortraitURL:    "http://localhost:9000/laboratory1/richter-6x9.jpg",
			Period:         "2002 - настоящее время",
			PolyphonyType:  "Минималистичный контрапункт",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     32.7,
					StdDev:        2.4,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     24.1,
					StdDev:        1.9,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     18.3,
					StdDev:        2.1,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     12.8,
					StdDev:        1.7,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     11.1,
					StdDev:        1.5,
				},
			},
			Biography: "Макс Рихтер — британский композитор-постминималист немецкого происхождения (род. 1966). Классически образованный выпускник Королевской академии музыки, он стал одним из самых влиятельных современных авторов, работая на стыке академической традиции и электронной музыки.",
		},
		{
			ID:             2,
			Name:           "Людвиг Ван Бетховен",
			AnalyzedWorks:  32,
			AnalysisCost:   890,
			TotalIntervals: 285430,
			PortraitURL:    "http://localhost:9000/laboratory1/bethoven.jpg",
			Period:         "1770-1827",
			PolyphonyType:  "Классика + контрапункт",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     28.4,
					StdDev:        3.2,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     26.8,
					StdDev:        2.8,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     22.1,
					StdDev:        2.5,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     15.3,
					StdDev:        2.1,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     7.4,
					StdDev:        1.8,
				},
			},
			Biography: "Великий немецкий композитор, пианист и дирижёр. Последний представитель венской классической школы. ключевая фигура западной классической музыки в период между классицизмом и романтизмом.",
		},
		{
			ID:             3,
			Name:           "Дзё Хисаиси",
			AnalyzedWorks:  24,
			AnalysisCost:   720,
			TotalIntervals: 215670,
			PortraitURL:    "http://localhost:9000/laboratory1/dze.jpg",
			Period:         "1981 - настоящее время",
			PolyphonyType:  "Остинато",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     30.2,
					StdDev:        2.1,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     25.6,
					StdDev:        1.9,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     20.8,
					StdDev:        2.0,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     14.7,
					StdDev:        1.6,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     8.7,
					StdDev:        1.4,
				},
			},
			Biography: "Японский композитор и музыкальный директор. Известен своими саундтреками к аниме-фильмам Хаяо Миядзаки. Сочетает элементы западной классической музыки с японскими традиционными мотивами.",
		},
		{
			ID:             4,
			Name:           "Пьер Булез",
			AnalyzedWorks:  16,
			AnalysisCost:   580,
			TotalIntervals: 172890,
			PortraitURL:    "http://localhost:9000/laboratory1/PierB.jpg",
			Period:         "1925-2016",
			PolyphonyType:  "Серийный контрапункт",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     35.8,
					StdDev:        4.2,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     18.9,
					StdDev:        3.1,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     16.4,
					StdDev:        2.8,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     19.2,
					StdDev:        3.0,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     9.7,
					StdDev:        2.1,
				},
			},
			Biography: "Французский композитор, дирижёр и музыкальный теоретик. Один из лидеров послевоенного авангарда. Разработал технику сериализма и был пионером электронной музыки.",
		},
		{
			ID:             5,
			Name:           "Дюк Эллингтон",
			AnalyzedWorks:  28,
			AnalysisCost:   820,
			TotalIntervals: 245320,
			PortraitURL:    "http://localhost:9000/laboratory1/DuckE.jpg",
			Period:         "1899-1974",
			PolyphonyType:  "Джазовая гетерофония",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     27.6,
					StdDev:        2.3,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     29.4,
					StdDev:        2.1,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     19.8,
					StdDev:        1.9,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     16.2,
					StdDev:        1.7,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     7.0,
					StdDev:        1.2,
				},
			},
			Biography: "Американский джазовый композитор, пианист и руководитель оркестра. Один из наиболее влиятельных фигур в истории джаза. Создал уникальный оркестровый звук и написал более 1000 произведений.",
		},
		{
			ID:             6,
			Name:           "Филип Гласс",
			AnalyzedWorks:  22,
			AnalysisCost:   750,
			TotalIntervals: 198560,
			PortraitURL:    "http://localhost:9000/laboratory1/PhilG.jpg",
			Period:         "1937 - настоящее время",
			PolyphonyType:  "Минималистичная гетерофония",
			IntervalStats: []IntervalStat{
				{
					IntervalGroup: "Унисоны и секунды",
					Frequency:     33.5,
					StdDev:        1.8,
				},
				{
					IntervalGroup: "Терции",
					Frequency:     22.3,
					StdDev:        1.6,
				},
				{
					IntervalGroup: "Кварты и квинты",
					Frequency:     21.7,
					StdDev:        1.7,
				},
				{
					IntervalGroup: "Сексты и септимы",
					Frequency:     13.9,
					StdDev:        1.4,
				},
				{
					IntervalGroup: "Октавы",
					Frequency:     8.6,
					StdDev:        1.2,
				},
			},
			Biography: "Американский композитор-минималист. Один из наиболее влиятельных композиторов конца XX - начала XXI века. Известен своими повторяющимися структурами и гипнотическими музыкальными паттернами.",
		},
	}

	return composerProfiles, nil
}

func (r *IntervalRepository) GetComposerIntervalDistribution(composerID int) (ComposerProfile, error) {
	composerProfiles, err := r.GetComposersWithIntervalStats()
	if err != nil {
		return ComposerProfile{}, err
	}

	for _, profile := range composerProfiles {
		if profile.ID == composerID {
			return profile, nil
		}
	}
	return ComposerProfile{}, fmt.Errorf("профиль композитора с ID %d не найден", composerID)
}

func (r *IntervalRepository) SearchComposersByPattern(pattern string) ([]ComposerProfile, error) {
	composerProfiles, err := r.GetComposersWithIntervalStats()
	if err != nil {
		return []ComposerProfile{}, err
	}

	var results []ComposerProfile
	for _, profile := range composerProfiles {
		if strings.Contains(strings.ToLower(profile.Name), strings.ToLower(pattern)) {
			results = append(results, profile)
		}
	}

	return results, nil
}

func (r *IntervalRepository) GetAttributionCandidates(workHash string) ([]ComposerProfile, error) {
	composerProfiles, err := r.GetComposersWithIntervalStats()
	if err != nil {
		return nil, err
	}

	if len(composerProfiles) > 3 {
		return composerProfiles[:3], nil
	}
	return composerProfiles, nil
}
