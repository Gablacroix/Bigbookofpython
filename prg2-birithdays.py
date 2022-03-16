import datetime
import random


def getBirthdays(numberOfBirthdays):
    # Возвращаем список объектов дат для случайных дней рождения
    birthdays = []
    for i in range(numberOfBirthdays):
        # год не играет роли - роли не играет главное чтобы был одинаков
        startOfYear = datetime.date(2001, 1, 1)
        # получаем случайный день года
        randomNumberOfDays = datetime.timedelta(random.randint(0, 364))
        birthday = startOfYear + randomNumberOfDays
        birthdays.append(birthday)
    return birthdays


def getMatch(birthdays):
    # Возвращаем обьект даты дня рождения встречающегося несколько раз в списке
    if len(birthdays) == len(set(birthdays)):
        return None  # Все дни рожденя различны
    # Сравниваем дни рождения поопарно
    for a, birthdayA in enumerate(birthdays):
        for b, birthdayB in enumerate(birthdays[a + 1:]):
            if birthdayA == birthdayB:
                return birthdayA # Возвращаем найденные соответствия.

# Отображаем вводную информацию:
print('''Парадокс дней рождения

Данная программа покажет нам сколько людей в группе имеют дни рождения в один день''')

# Создаем кортеж названий месяцев
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

while True: # запрашиваем пока пользователь не введет допустимое значение
    print('Сколько дней рождения сгенерировать ? ( Макс 100) ')
    response = input('> ')
    if response.isdecimal() and (0 < int(response) <= 100):
        numBDays = int(response)
        break # пользователь ввел допустимое
print()

# Генерируем и отображаем дни рождения
print( 'Создано', numBDays, 'ДР')
birthdays = getBirthdays(numBDays)
for i, birthday in enumerate(birthdays):
    if i !=0:
        # Выводим запятую для каждого дня рождения после первого.
        print(', ', end='')
    monthName = MONTHS[birthday.month - 1]
    dateText = '{} {}'.format(monthName, birthday.day)
    print(dateText, end='')
print()
print()

#Выясняем,  встречаются ли 2 сопадающих
match = getMatch(birthdays)

# Отображаем результаты:
print('В текущей симуляции, ', end='')
if match != None:
    monthName =MONTHS[match.month - 1]
    dateText = '{} {}'.format(monthName, match.day)
    print('несколько человек имеют дни рождения в', dateText)
else:
    print('совпадений нет')
print()

# Проводим 100,000 симуляций
print('Генерируем', numBDays, ' случайных дней рождения 100,000 раз...')
input('Нажмете enter чтобы начать')

print('Запустим еще 100,000 симуляций')
simMatch = 0
for i in range(100_000):
    # Отображаем о ходе выполнения каждые 10000 операций
    if 1%10_000 == 0:
        print(i, 'симуляция запущена...')
    birthdays = getBirthdays(numBDays)
    if getMatch(birthdays) != None:
        simMatch = simMatch + 1
print('100_000 симуляций идет')

# Отображаем результаты имитации
probability = round(simMatch / 100_000 * 100, 2)
print('После 100,000 симуляций', numBDays, 'человек имеют')
print('совпадающие дни рождения в этой группе', simMatch, 'раз')
print('для', numBDays, 'человек шанс совпадения составляет',probability, '% ')
print('иметь собпадение дней рождения в этой группе')