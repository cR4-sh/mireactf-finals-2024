package handlers

import (
	"encoding/base64"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"web/database"
	"web/logic"
	"web/models"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func validate(c *gin.Context, department string) bool {
	cookies := c.Request.Cookies()

	for _, cookie := range cookies {
		fmt.Println("Cookie:", cookie.Name, "=", cookie.Value)
	}
	cookie, err := c.Cookie("department")
	if err != nil {
		if err == http.ErrNoCookie {
			return false
		}
		return false
	}
	dep, err := logic.GetAndVerificate(cookie)
	if err != nil {
		return false
	}
	if dep != department {
		return false
	}
	return true
}

func PostRegister(c *gin.Context) {
	var user models.User
	user.Username = c.PostForm("username")
	user.Password = c.PostForm("password")
	session := sessions.Default(c)
	if user.Username == "" {
		c.HTML(http.StatusOK, "register.html", gin.H{"error": "Введите имя!"})
	}
	if user.Password == "" {
		c.HTML(http.StatusOK, "register.html", gin.H{"error": "Введите пароль!"})
	}
	for _, u := range database.GetAllUser() {
		if u.Username == user.Username {
			c.HTML(http.StatusOK, "register.html", gin.H{"error": "Такой пользователь уже существует!"})
			return
		}
	}
	database.CreateUser(user)
	session.Set("username", user.Username)
	session.Save()
	c.Redirect(http.StatusFound, "/")
}

func GetRegister(c *gin.Context) {
	c.HTML(200, "register.html", gin.H{})
}

func PostLogin(c *gin.Context) {
	var user models.User
	user.Username = c.PostForm("username")
	user.Password = c.PostForm("password")
	session := sessions.Default(c)

	for _, u := range database.GetAllUser() {
		if u.Username == user.Username && u.Password == user.Password {
			session.Set("username", user.Username)
			session.Save()
			user := logic.GetUserFromSession(c)
			if user.Department != "" {
				c.SetCookie("department", logic.GetDepartmentCookie(user.Department), 3600, "/", "", true, true)
			}
			c.Redirect(http.StatusFound, "/")
			return
		}
	}

	c.HTML(http.StatusOK, "login.html", gin.H{"error": "Неправильное имя пользователя или пароль"})

}

func GetLogin(c *gin.Context) {
	c.HTML(200, "login.html", gin.H{})
}

func GetMainPage(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	if user.Department != "" {
		c.SetCookie("department", logic.GetDepartmentCookie(user.Department), 3600, "/", "", true, true)
	}
	cookie, _ := c.Cookie("department")
	dep, _ := logic.GetAndVerificate(cookie)
	objects := database.GetSCPbyDepartment(dep)
	c.HTML(200, "main_page.html", gin.H{"user": user, "objects": objects})
}

func GetObject(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	object := database.GetSCPByName(c.Param("object"))
	if !validate(c, object.Department) {
		c.String(200, "Access denied!!!")
		return
	}
	if object == (models.SCP{}) {
		c.String(http.StatusNotFound, "Object not found")
		return
	}
	imageData, err := os.ReadFile("./secret-data/images/" + object.ImagePath)
	if err != nil {
		imageData, err = os.ReadFile("./resources/images/404.png")
		if err != nil {
			c.String(500, "Error reading image")
			return
		}
	}

	description, err := os.ReadFile("./secret-data/description/" + object.DescryptionPath)
	if err != nil {
		log.Print(err.Error())
		c.String(http.StatusInternalServerError, "Error reading descrptoin")
		return
	}
	log.Print(string(description))
	encodedImage := base64.StdEncoding.EncodeToString(imageData)
	c.HTML(200, "object.html", gin.H{"name": object.Name, "imagedata": encodedImage, "description": strings.Split(string(description), "\n"), "user": user})
}

func PostCreateSCP(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	if user.Department == "" {
		c.HTML(http.StatusOK, "create_scp.html", gin.H{"user": user, "error": "Чтобы создавать документы, нужно быть в отделе!"})
		return
	}

	name := c.PostForm("name")
	description := c.PostForm("description")
	_, header, _ := c.Request.FormFile("image")
	image_name := ""

	if header != nil {
		maxSize := int64(1024 * 1024 * 10)

		fileSize := header.Size
		if fileSize > maxSize {
			c.String(http.StatusBadRequest, "Превышен максимальный размер файла (10MB)")
			return
		}
	}

	image, err := c.FormFile("image")
	for _, s := range database.GetAll() {
		if s.Name == name {
			c.HTML(http.StatusOK, "create_scp.html", gin.H{"user": user, "error": "Такой объект уже существует!"})
			return
		}
	}

	if err == nil {
		ImageFilePath := filepath.Join("./secret-data/images", image.Filename) // ImageFilePath := filepath.Join("./secret-data/images", filepath.Base(image.Filename))
		file, err := os.Create(ImageFilePath)
		if err != nil {
			c.String(500, "Ошибка при создании файла для изображения")
			return
		}
		defer file.Close()
		src, err := image.Open()
		if err != nil {
			c.String(500, "Ошибка при открытии файла: %v", err)
			return
		}
		defer src.Close()

		if _, err := io.Copy(file, src); err != nil {
			c.String(500, "Ошибка при сохранении изображения")
			return
		}
		image_name = image.Filename
	}

	txtFilePath := filepath.Join("./secret-data/description", name) // txtFilePath := filepath.Join("./secret-data/description", filepath.Base(name))
	txtFile, err := os.OpenFile(txtFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		c.String(500, "Ошибка при открытии файла")
		return
	}
	defer txtFile.Close()

	if _, err := txtFile.WriteString(description); err != nil {
		c.String(500, "Ошибка при записи в файл")
		return
	}

	database.CreateSCP(models.SCP{DescryptionPath: name, ImagePath: image_name, Name: name, Department: user.Department})

	c.Redirect(302, "/")
}

func GetCreateSCP(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	c.HTML(200, "create_scp.html", gin.H{"user": user})
}

func Department(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	if user.Department != "" {
		c.SetCookie("department", logic.GetDepartmentCookie(user.Department), 3600, "/", "", true, true)
	}
	c.HTML(200, "department.html", gin.H{"user": user, "users": database.GetDepartmentStaff(user.Department)})
}

func GetCreateDepartment(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	c.HTML(200, "create_department.html", gin.H{"user": user})
}

func PostCreateDepartment(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	name_department := c.PostForm("name_department")
	for _, u := range database.GetAllUser() {
		if u.Department == name_department {
			c.HTML(http.StatusOK, "create_department.html", gin.H{"user": user, "error": "Такой отдел уже существует!"})
			return
		}
	}
	database.ChangeDepartment(user, name_department)
	c.Redirect(http.StatusFound, "/")
}

func Invite(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	username := c.PostForm("username")
	if user.Department == "" {
		c.HTML(http.StatusOK, "department.html", gin.H{"users": database.GetDepartmentStaff(user.Department), "user": user, "error": "Вы не состоите в отделе!"})
		return
	}
	guest := database.GetUserByName(username)
	if guest.Username == "" {
		c.HTML(http.StatusOK, "department.html", gin.H{"users": database.GetDepartmentStaff(user.Department), "user": user, "error": "Пользователь с таким именем не найден!"})
		return
	}
	if guest.Department != "" {
		c.HTML(http.StatusOK, "department.html", gin.H{"users": database.GetDepartmentStaff(user.Department), "user": user, "error": "Пользователь уже состоит в отделе ", "guest": guest})
		return
	}
	database.ChangeDepartment(guest, user.Department)
	c.Redirect(http.StatusFound, "/department")
}

func Logout(c *gin.Context) {
	logic.ExitSession(c)
	c.SetCookie("department", "", -1, "/", "", false, true)
	c.Redirect(http.StatusFound, "/login")
}

func ExitFromDepartment(c *gin.Context) {
	user := logic.GetUserFromSession(c)
	database.ChangeDepartment(user, "")
	c.SetCookie("department", "", -1, "/", "", false, true)
	c.Redirect(http.StatusFound, "/")
}
