from time import sleep
import json

def new_idea(dct):
    print("Тема и элемент")
    inp = input().split()
    if len(inp)>1:
        theme = inp[0].capitalize()
        idea = " ".join(inp[1:])
        if theme not in dct:
            dct[theme] = []
        dct[theme].append(idea)
        save(dct)
    else:
        print("Ошибка, попробуйте снова")

def delete(dct):
    print("Тема и номер удаляемого элемента")
    inp = input().split()
    if len(inp)==2 and inp[1].isdigit():
        theme = inp[0].capitalize()
        num = int(inp[1])
        if len(dct[theme])>=num and num>=1 and theme in dct:
            dct[theme].pop(num-1)
        save(dct)
    else:
        print("Ошибка, попробуйте снова")


def vyvod(dct):
    print("Ваш список:")
    print("\n")
    for theme in dct:
        if len(dct[theme])>=1:
            print(theme)
        for number,element in enumerate(dct[theme],start=1):
            print(f'{number}.{element}')

def save(dct):
    with open("tasks.json", "w", encoding="utf-8") as file:
        json.dump(dct, file, ensure_ascii=False, indent=4)


print("Привет! Это to-do list, твой помощник.")
sleep(1)
try:
    with open("tasks.json", "r", encoding="utf-8") as file:
        ideas = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    ideas = {}
while True:
    if len(ideas)>0:
        vyvod(ideas)
    print("Выберите действие:","1 - add element","2 - delete element","3 - exit", sep = "\n")
    value = int(input())
    match value:
        case 1:
            new_idea(ideas)
        case 2:
            delete(ideas)
        case 3:
            exit()
        case _ :
            print("Несуществующая команда") 