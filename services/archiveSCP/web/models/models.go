package models

type SCP struct {
	Name            string
	DescryptionPath string
	ImagePath       string
	Department      string
}

type User struct {
	Username   string
	Password   string
	Department string
}
