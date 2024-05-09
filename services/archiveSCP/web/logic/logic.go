package logic

import (
	"crypto/md5"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"net/url"
	"strings"
	"web/database"
	"web/models"

	"crypto/rand"
	"fmt"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func GenerateRandomKey() string {
	buffer := make([]byte, 32)

	if _, err := rand.Read(buffer); err != nil {
		return ""
	}

	key := hex.EncodeToString(buffer)

	return key
}

var secretDep string = GenerateRandomKey()

func AuthRequired(c *gin.Context) {
	session := sessions.Default(c)
	username := session.Get("username")
	if username == nil {
		c.Redirect(http.StatusFound, "/login")
		return
	}
	c.Next()
}

func AccessVerification(c *gin.Context, object models.SCP) bool {
	result := map[string]interface{}{"access": false}
	response, err := http.Get("http://" + c.Request.Host + "/validate")
	if err != nil {
		return false
	}
	defer response.Body.Close()
	json.NewDecoder(response.Body).Decode(&result)
	if access, ok := result["access"].(bool); ok {
		return access
	} else {
		return false
	}
}

func GetUserFromSession(c *gin.Context) models.User {
	session := sessions.Default(c)
	username := session.Get("username")
	if username != nil {
		return database.GetUserByName(username.(string))
	}
	return models.User{}
}

func ExitSession(c *gin.Context) {
	session := sessions.Default(c)
	session.Delete("username")
	session.Save()
}

func MyParseQuery(rawQuery string) (map[string]string, error) {
	decodedQuery, err := url.QueryUnescape(rawQuery)
	if err != nil {
		return nil, fmt.Errorf("ошибка декодирования строки: %v", err)
	}

	values := make(map[string]string)
	params := strings.Split(decodedQuery, "&")
	for _, param := range params {
		keyValue := strings.SplitN(param, "=", 2)
		if len(keyValue) != 2 {
			return nil, fmt.Errorf("некорректный формат параметра: %s", param)
		}
		key, value := keyValue[0], keyValue[1]
		values[key] = value
	}
	return values, nil
}

func GetAndVerificate(c string) (string, error) {
	hash := md5.New()
	parts := strings.SplitN(c, ".", 2)
	if len(parts) != 2 {
		// Если точка не найдена, возвращаем пустые строки
		return "", fmt.Errorf("некорректный формат куки")
	}
	sig := parts[0]
	data, err := base64.StdEncoding.DecodeString(parts[1])
	if err != nil {
		return "", fmt.Errorf("ошибка декодирования base64")
	}
	urldecode, err := url.QueryUnescape(string(data))
	if err != nil {
		return "", fmt.Errorf("ошибка декодирования urlencode")
	}
	hash.Write([]byte(secretDep + urldecode))
	md5Str := hex.EncodeToString(hash.Sum(nil))
	if md5Str != sig {
		return "", fmt.Errorf("неверная сигнатура")
	}
	parsedValues, err := MyParseQuery(string(data))
	if err != nil {
		return "", fmt.Errorf("ошибка при парсинге строки запроса")
	}
	department, ok := parsedValues["department"]
	if !ok {
		return "", fmt.Errorf("department не найден")
	}
	return department, nil
}

func GetDepartmentCookie(department string) string {
	hash := md5.New()
	payload := "department=" + department
	hash.Write([]byte(secretDep + payload))
	sig := hex.EncodeToString(hash.Sum(nil))
	return sig + "." + base64.StdEncoding.EncodeToString([]byte(payload))
}
