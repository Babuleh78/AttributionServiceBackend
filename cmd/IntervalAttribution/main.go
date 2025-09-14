package main

import (
	"backend-design/internal/api"
	"log"

)


func main(){
	log.Println("app start")
	api.StartServer()
	log.Println("app term")
}