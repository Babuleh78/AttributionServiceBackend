package api

import (
	"backend-design/internal/app/handler"
	"backend-design/internal/app/repository"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func StartServer() {
	log.Println("Starting attribution analysis server")

	intervalRepo, err := repository.NewIntervalRepository()
	if err != nil {
		logrus.Error("ошибка инициализации репозитория частотности интервалов")
	}

	attributionHandler := handler.NewAttributionHandler(intervalRepo)

	r := gin.Default()

	r.LoadHTMLGlob("../../templates/*")
	r.Static("/static", "../../resources")

	r.GET("/composers", attributionHandler.GetComposersWithStats)
	r.GET("/composer/:id", attributionHandler.GetComposerIntervalProfile)
	r.GET("/attribution-candidates", attributionHandler.ViewAttributionResults)

	r.Run()
	log.Println("Attribution server stopped")
}
