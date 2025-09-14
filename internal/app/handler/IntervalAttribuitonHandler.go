package handler

import (
	"backend-design/internal/app/repository"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

type AttributionHandler struct {
	IntervalRepo *repository.IntervalRepository
}

func NewAttributionHandler(r *repository.IntervalRepository) *AttributionHandler {
	return &AttributionHandler{
		IntervalRepo: r,
	}
}

func (h *AttributionHandler) GetComposersWithStats(ctx *gin.Context) {
	var composers []repository.ComposerProfile
	var err error

	searchQuery := ctx.Query("query")
	if searchQuery == "" {
		composers, err = h.IntervalRepo.GetComposersWithIntervalStats()
		if err != nil {
			logrus.Error("Ошибка получения статистики композиторов: ", err)
		}
	} else {
		composers, err = h.IntervalRepo.SearchComposersByPattern(searchQuery)
		if err != nil {
			logrus.Error("Ошибка поиска композиторов: ", err)
		}
	}

	attributionCandidates, err := h.IntervalRepo.GetAttributionCandidates("")
	candidateCount := 0
	if err != nil {
		logrus.Error("Ошибка получения кандидатов атрибуции: ", err)
	} else {
		candidateCount = len(attributionCandidates)
	}

	ctx.HTML(http.StatusOK, "main_page.html", gin.H{
		"composerProfiles": composers,
		"searchPattern":    searchQuery,
		"candidateCount":   candidateCount,
	})
}

func (h *AttributionHandler) GetComposerIntervalProfile(ctx *gin.Context) {
	idStr := ctx.Param("id")
	composerID, err := strconv.Atoi(idStr)
	if err != nil {
		logrus.Error("Неверный ID композитора: ", err)
	}

	intervalProfile, err := h.IntervalRepo.GetComposerIntervalDistribution(composerID)
	if err != nil {
		logrus.Error("Ошибка получения профиля интервалов: ", err)
	}

	ctx.HTML(http.StatusOK, "composer_profile.html", gin.H{
		"composer": intervalProfile,
	})
}

func (h *AttributionHandler) ViewAttributionResults(ctx *gin.Context) {
    attributionCandidates, err := h.IntervalRepo.GetAttributionCandidates("")
    if err != nil {
        logrus.Error("Ошибка получения кандидатов атрибуции: ", err)
    }

    type CandidateWithPrice struct {
        repository.ComposerProfile
        CalculatedPrice float64
    }

    var candidatesWithPrices []CandidateWithPrice
    totalSum := 0.0

    for _, candidate := range attributionCandidates {
        calculatedPrice := float64(candidate.AnalysisCost) * 300 / 60
        totalSum += calculatedPrice
        
        candidatesWithPrices = append(candidatesWithPrices, CandidateWithPrice{
            ComposerProfile: candidate,
            CalculatedPrice: calculatedPrice,
        })
    }

    ctx.HTML(http.StatusOK, "attribution_candidates.html", gin.H{
        "attributionCandidates": candidatesWithPrices,
        "totalSum":              totalSum,
    })
}

func (h *AttributionHandler) ViewAttribtuionCandidatesCount(ctx *gin.Context) {
	attributionCandidates, err := h.IntervalRepo.GetAttributionCandidates("")
	if err != nil {
		logrus.Error("Ошибка получения кандидатов атрибуции: ", err)
	}

	ctx.HTML(http.StatusOK, "attribution_candidates.html", gin.H{
		"candidateCount": len(attributionCandidates),
	})
}
