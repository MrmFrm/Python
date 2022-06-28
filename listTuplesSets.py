#list 
courses = ['History', 'Math', 'Physics', 'CompSci']
print(courses)
print(len(courses)) #länge
#slicing
print(courses[1]) # startet bei 0, also wird hier Math ausgegeben
print(courses[-1]) #last item in the list
print(courses[-2]) # second last
print(courses[0:2]) # 0 und 1, 2 ist nicht inkludiert
print(courses[:2]) # 0 und 1, 2 ist nicht inkludiert
print(courses[2:]) # von 2 bis Ende
#add
courses.append('Art')
print(courses)
courses.insert(0,'German') # nicht überschreiben, nur einfügen
print(courses)
courses_2=['Spain','English']
courses.insert(0,courses_2) # list in der liste
courses = ['History', 'Math', 'Physics', 'CompSci']
courses.extend(courses_2) 
popped = courses.pop() #letztes Element
print(courses) #letztes Element durch pop Befehl entfernt
print(courses[0]) #Spain, English
courses.reverse()
courses.sort() #alphabetic order, increasing numbers#courses.sort(reverse=True)
#courses.sort ändert Liste, sorted(courses) ändert sie nicht
print(courses)
print('Art' in courses)#false
print('art' in courses)#false
course_str = ' - '.join(courses) # list in string
course_list = course_str.split(' - ')
print(course_str)
print(course_list)
print(courses.index('Math'))



#tuples, we can't modify tuples, immutable
list_1 = ['a', 'b', 'c']
list_2 = list_1
list_1[0] = 'neu'
print(list_1)
print(list_2)#mutable!
tuple_1=('History', 'Math', 'Physics')
tuple_2=('History', 'Math', 'Physics')
#tuple_1[0] = 'neu' --> Fehlermeldung



# Sets --> immer geordnet + ohne Duplikate (Membership Test)
courses_sets = {'d','a', 'g', 'g'}
print(courses_sets)

#Dictionaries
student = {'name':'John', 'age': 25, 'courses':['Math', 'CompSci']}
print(student['name']) # fehlermeldung bei fehlendem Eintrag
print(student.get('name'))
print(student.get('Height', 'not found')) # not found bei fehlendem Eintrag
student['phone'] = '444 4444'
#update multiple values at a time
student.update({'name': 'Jane', 'age':26, 'phone': '555-5555'})
del student['phone']
age =student.pop('age')
print(age)

for key, value in student.items():
    print(key, value)


