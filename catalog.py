from bs4 import BeautifulSoup 
import json
import requests
import re

def read_file(path):
    file = open(path, encoding='utf-8')
    data = file.read()
    file.close()
    return data

"""
    construct dict with
    course number
    course name
    course description
    unit count
    prerequisites
"""
def parse_course(name, desc, dept):
    course_data = {}
    course_data['dept'] = dept

    idx_of_last_open_paren = name.rfind('(')
    idx_of_last_close_paren = name.rfind(')')
    units_str = name[idx_of_last_open_paren + 1:idx_of_last_close_paren]

    name = name[:idx_of_last_open_paren - 1]
    split_name = re.split(r'\.\s', name)
    course_data['name'] = split_name[1]
    course_data['number'] = split_name[0]

    try:
        course_data['units'] = int(units_str)
    except ValueError:
        course_data['units'] = None

    split_desc = re.split(r'\sPrerequisites:\s', desc)
    course_data['description'] = split_desc[0]
    if len(split_desc) > 1:
        course_data['prerequisites'] = split_desc[1]
    else:
        course_data['prerequisites'] = None

    return course_data
    

"""
    parse the department page
    get list of courses
"""
def parse_dept(soup):

    dept = soup.find('h1')
    names = soup.find_all('p', {'class': 'course-name'})

    courses = []
    for name in names:
        desc = name.find_next('p')

        try:
            course = parse_course(name.text, desc.text, dept.text)
            courses.append(course)
            print('parsed ' + course['name'] + ' from ' + course['dept'])
        except:
            print('error parsing ' + name.text)

    return courses

"""
    get list of department urls
"""
def get_dept_urls(soup):
    depts = []
    for link in soup.find_all('a', string='courses'):
        depts.append('http://catalog.ucsd.edu/front/' + link.get('href'))
    return depts

def main():

   depts_page = requests.get('https://catalog.ucsd.edu/front/courses.html')
   depts_page = BeautifulSoup(depts_page.content, 'html.parser')
   dept_urls = get_dept_urls(depts_page)
   
   all_courses = []

   for url in dept_urls:
       dept_soup = BeautifulSoup(requests.get(url).content, 'html.parser')
       dept_data = parse_dept(dept_soup) 
       all_courses.extend(dept_data) 

   with open('courses_raw.json', 'w') as f:
        json.dump(all_courses, f)

if __name__ == '__main__':
    main()
