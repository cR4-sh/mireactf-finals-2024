package main

import (
	"web/database"
	"web/handlers"
	"web/logic"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
)

func main() {
	secret := logic.GenerateRandomKey()
	store := cookie.NewStore([]byte(secret))
	database.InitDataBase()
	router := gin.Default()
	router.Use(sessions.Sessions("mysession", store))
	router.LoadHTMLGlob("./templates/*.html")
	router.Static("/resources", "./resources")
	router.Use(gin.Recovery())
	router.Use(gin.Logger())
	router.GET("/", logic.AuthRequired, handlers.GetMainPage)
	router.GET("/:object", logic.AuthRequired, handlers.GetObject)
	// router.GET("/validate", handlers.Validate)
	router.GET("/register", handlers.GetRegister)
	router.POST("/register", handlers.PostRegister)
	router.GET("/login", handlers.GetLogin)
	router.POST("/login", handlers.PostLogin)
	router.GET("/create_scp", logic.AuthRequired, handlers.GetCreateSCP)
	router.POST("/create_scp", logic.AuthRequired, handlers.PostCreateSCP)
	router.GET("/department", logic.AuthRequired, handlers.Department)
	router.GET("/create_department", logic.AuthRequired, handlers.GetCreateDepartment)
	router.POST("/create_department", logic.AuthRequired, handlers.PostCreateDepartment)
	router.POST("/invite", logic.AuthRequired, handlers.Invite)
	router.GET("/logout", logic.AuthRequired, handlers.Logout)
	router.GET("/exit", logic.AuthRequired, handlers.ExitFromDepartment)
	router.Run(":8000")
}
