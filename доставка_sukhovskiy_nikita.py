# -*- coding: utf-8 -*-
"""Доставка_Nikita.ipynb



# Задание:

1. Основная задача аналитиков в нашей компании - растить бизнес. Иногда мы сами не знаем где прячутся эти точки кратного
роста, поэтому порой приходится кранчить данные и искать зависимости/аномалии, генерировать гипотезы в процессе и потом
предлагать проекты. Мы дадим доступ к базе со срезом транзакций. Твое задание: найти все интересные на твой взгляд
инсайты и представь их в любом удобном виде (ноутбук желательно приложить).

## Ответ на задание №1

Схема таблиц и полей
Приведение основные поля. В таблицах чуть больше колонок, но те, которых нет в описании, не такие важные

###### Таблица

Поле
Расшифровка 

###### orders

Id
id заказа


created_at
timestamp создания заказа на сайте


delivery_window_id
id слота доставки


item_total
Сумма всех товаров в корзине (средний чек)


promo_total
Сумма промо-кода на товары в корзине


cost
Изначальная стоимость доставки


total_cost
Финальная стоимость доставки (отличается, если был применен промо-код на доставку.
Если промокода не было, то cost=total_cost)


ship_address_id
id адреса доставки (ключ к addresses.id)


shipped_at
timestamp доставки заказа


state
состояние доставки (shipped, canceled и тд)


store_id
id магазина


total_quantity
Количество единиц товара


total_weight
Вес заказа , г.


user_id
id пользователя


###### delivery_windows

id
id слота доставки (ключ к orders.delivery_window_id)


starts_at
timestamp начала слота доставки


ends_at
timestamp конца слота доставки


store_id
ID магазина

###### stores

id
ID магазина


city
ID города


retailer_id
ID ритейлера

###### addresses

id
ID адреса (ключ к orders.ship_address_id)


lat
latitude


lon
longitude


###### replacements

item_id
id товара, который был заменен


order_id
id заказа, в котором была замена


state
статус (замена)


###### cancellations

item_id
id товара, который был отменен


order_id
id заказа, в котором была отмена


state
статус (отмена)
"""

# Соберем данные которые доступны нам и создадим из них таблицы, для дальнейшей работы.
import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import datetime as dt


accesses = {'host': 'rc1c-fhrb9f1e0l9g611h.mdb.yandexcloud.net',
            'port': '6432',
            'dbname': 'hr-analytics',
            'sslmode': 'require',
            'user': 'analytics',
            'password': 'HRanalytics'
            }

#  !pip install psycopg2-binary
connection = psycopg2.connect(database=accesses['dbname'],
                             user=accesses['user'],
                             password=accesses['password'],
                             host=accesses['host'],
                             port=accesses['port'],
                             sslmode=accesses['sslmode'])
cursor = connection.cursor()

query = """SELECT *
            FROM orders"""

cursor.execute(query)
result = cursor.fetchall()

cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
orders = pd.DataFrame(result, columns = columns)
orders.head()

query = """SELECT *
            FROM delivery_windows"""

cursor.execute(query)
result = cursor.fetchall()
cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
delivery_windows = pd.DataFrame(result, columns = columns)
delivery_windows.head()

query = """SELECT *
            FROM stores"""

cursor.execute(query)
result = cursor.fetchall()
cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
stores = pd.DataFrame(result, columns = columns)
stores.head()

query = """SELECT *
            FROM addresses"""

cursor.execute(query)
result = cursor.fetchall()
cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
addresses = pd.DataFrame(result, columns = columns)
addresses.head()

query = """SELECT *
            FROM replacements"""

cursor.execute(query)
result = cursor.fetchall()
cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
replacements = pd.DataFrame(result, columns = columns)
replacements.head()

query = """SELECT *
            FROM cancellations"""

cursor.execute(query)
result = cursor.fetchall()
cursor.description

columns = []
for desc in cursor.description:
    columns.append(desc[0])
cancellations = pd.DataFrame(result, columns = columns)
cancellations.head()

"""#### Данные собраны, начинаем работать с ними.

Для бизнеса важны два параметра: 
1. Увеличение прибыли
2. Сокращение издержек.

Остальное, — это уже производные от этих двух параметров. 
Мы можем увеличивать продажи в одни руки, тем самым увеличивая прибыль или можем сокращать время доставки, тем самым 
повышая лояльность и увеличивая прибыль в будущем и т.д.

## 1. Проблемы с данными
Во время работы с данными обнаружились проблемы их качества, в частности:
1. Есть доставки с нулевым значением стоимости доставки
2. Есть доставки с нулевым значением количества заказанных товаров
3. Есть доставки с нулевым значение веса доставки


Если эти данные заполняют сотрудники, то стоит обратить внимание руководства на то, что не все сотрудники утруждают себя
 заполнением этих пунктов, что может повлиять на качество работы аналитиков и их выводы. 
Если эти данные подгружаются автоматически из какого-либо источника, то стоит проверить 
в чем произощел сбой и исправить это.
"""

#  Сгруппируем таблицы 'orders' и 'stores' для изучения есть ли выраженное количество
#  и вес заказываемых товаров по городам/ретейлам/магазинам.
quantity_and_weight = orders.merge(stores, left_on='store_id', right_on='id')
quantity_and_weight_shipped = quantity_and_weight[quantity_and_weight['state'] == 'shipped']
quantity_and_weight_shipped.head()

#  Видим иготовую стоимость товара total_cost = 0.0, при отправленном заказе state = shipped.

#  Посмотрим какие есть значения по весу и по количеству товаров в заказе.
city_quantity = quantity_and_weight_shipped[['total_quantity', 'total_weight', 'city']]
city_quantity.sort_values(by = 'total_quantity', ascending = False).head(10)

"""Допускаем, что компания может доставить несколько тонн товара, с сумарным количеством десятки тысяч единиц :)"""

# Проверим, вдруг у нас в скидку закралось повышение цены, а не понижение
orders.loc[orders.loc[:, 'promo_total'] > 0].count()

"""Данные посмотрели, некоторые ошибки обнаружили. Удалять данные не будем, так как может удалить данные которые нам пригодятся при последующих исследованиях.

## 2. Проблемы со временем доставки

Посмотрим есть ли у нас проблемы со временем доставки для различных городов.
"""

# Соединим две таблицы 'orders' и 'delivery_windows' чтобы сравнить попадает ли время доставки в окно доставки, которое выбрал покупатель.

time_out_delivery = orders.merge(delivery_windows, left_on = 'delivery_window_id', right_on = 'id')
time_out_delivery_shipped = time_out_delivery[time_out_delivery['state'] == 'shipped'] # Выберем только те строки, в которых доставка была осуществлена
time_out_delivery_shipped.head()

# Создадим таблицу в которой укажем время доставки и время окна доставки
late_delivery = pd.DataFrame(data=time_out_delivery_shipped['shipped_at'])
late_delivery['starts_at'] = time_out_delivery_shipped['starts_at']
late_delivery['ends_at'] = time_out_delivery_shipped['ends_at']

# Добавим к получившейся таблице сравнительный столбец, в котором сравним время окна доставки с фактическим временем доставки
late_delivery['late'] = late_delivery['ends_at'] < late_delivery['shipped_at']
late_delivery['early'] = late_delivery['starts_at'] > late_delivery['shipped_at']

# Посчитаем количество заказов которые опоздали
count_late = late_delivery[late_delivery['late'] == True]
percent_late = (count_late['late'].count() / late_delivery['shipped_at'].count())

# Посчитаем количество заказов которые пришли раньше
count_early = late_delivery[late_delivery['early'] == True]
percent_early = (count_early['early'].count() / late_delivery['shipped_at'].count())

# Посчитаем общее количество заказов которые были доставлены и долю от заказов которые не попали в окно доставки
print('Всего выполненных заказов:', late_delivery['shipped_at'].count(), '|' , '100%')
print('Заказов которые пришли раньше:', count_early['early'].count(), '|', '{:.2%}'.format(percent_early) )
print('Заказов которые опоздали:', count_late['late'].count(), '|', '{:.2%}'.format(percent_late) ) 
print('Итого заказов которые пришли не во время окна доставки:',count_early['early'].count()+count_late['late'].count(), '|', '{:.2%}'.format(percent_early+percent_late) )

"""#### Таким образом видим, что каждый четвертый заказ не попадает в окно доставки.
Да, доставка может опоздать незначительно, кто-то на пару минут, кто-то на пару секунд. Однако, когда заказывается доставка, покупателем ожидается, что она прибудет не в крайние сроки.

Разберем это проблемное место по городам и ретейлам.
"""

# Добавим в таблицу данные по городам и ретейлам
late_delivery['store_id'] = time_out_delivery_shipped['store_id_x']
late_delivery_stores = late_delivery.merge(stores, left_on = 'store_id', right_on = 'id')
late_delivery_stores.head()

# Сгруппируем и выведем наши данные по количеству опазданий по городам.
true_late_delivery_stores = late_delivery_stores[late_delivery_stores['late'] == True]
count_true_late_delivery_stores = true_late_delivery_stores.groupby('city')['late'].count()
count_true_late_delivery_stores

citys = []
for i in true_late_delivery_stores['city'].unique():
    citys.append(str(i))

# Выведем столбчатую диаграмму по абсолютному количеству просроченных заказов по городам.
fig, ax = plt.subplots()

plt.title('Абсолютное количестов просроченных заказов по городам, шт', size = 18)
plt.xlabel('ID города', size = 12)
plt.ylabel('Количество опазадний', size = 12)
plt.grid()

ax.bar(citys, true_late_delivery_stores.groupby('city')['late'].count(), color = 'brown')
ax.set_xticks(citys)

fig.set_figwidth(12)   
fig.set_figheight(6)    

plt.show()

# Сгруппируем и выведем наши данные по количеству ранних доставок по городам.
true_early_delivery_stores = late_delivery_stores[late_delivery_stores['early'] == True]
count_true_early_delivery_stores = true_early_delivery_stores.groupby('city')['early'].count()
count_true_early_delivery_stores

fig, ax = plt.subplots()

plt.title('Абсолютное количестов ранних заказов по городам, шт', size = 18)
plt.xlabel('ID города', size = 12)
plt.ylabel('Количество ранних доставок', size = 12)
plt.grid()

ax.bar(citys, true_early_delivery_stores.groupby('city')['early'].count(), color = 'b')
ax.set_xticks(citys)

fig.set_figwidth(12)   
fig.set_figheight(6)    

plt.show()

"""
Если рассматривать эти графики, то видим что наибольшее количество заказов которые пришли вне слота доставки это заказы в городе ID=1

Однако, надо рассмотреть какую долю такие заказы занимают среди всех доставок по городам, посмотрим ниже."""

# Рассмотрим долю доставок которые опоздали или пришли раньше слота доставки по городам
percent_late_by_city = ((true_late_delivery_stores.groupby('city')['late'].count() * 100) / late_delivery_stores.groupby('city')['shipped_at'].count())
percent_early_by_city = ((true_early_delivery_stores.groupby('city')['early'].count() * 100) / late_delivery_stores.groupby('city')['shipped_at'].count())

fig, ax = plt.subplots()

plt.title('Доля просроченных заказов по городам, %', size = 18)
plt.xlabel('ID города', size = 12)
plt.ylabel('Процент опазадний', size = 12)
plt.grid()

ax.bar(citys, percent_late_by_city, color = 'orange')
ax.set_xticks(citys)

fig.set_figwidth(12)   
fig.set_figheight(6)    

plt.show()

fig, ax = plt.subplots()

plt.title('Доля ранних заказов по городам, %', size = 18)
plt.xlabel('ID города', size = 12)
plt.ylabel('Процент ранних доставок', size = 12)
plt.grid()

ax.bar(citys, percent_early_by_city, color = 'c')
ax.set_xticks(citys)

fig.set_figwidth(12)   
fig.set_figheight(6)    

plt.show()

"""#### На графиках видим, что в количественном значении наибольшие проблемы с доставкой у нас наблюдаются в городе ID=1. Однако, в долевом представлении стоит уделить внимание городу ID=2, чтобы сотрудники следили за временем начала окна доставки и не привозили заказ раньше.
_______________________________________________________________________________________________________________________________

### Что еще можно покопать в данном направлении:
1. По каким дням недели чаще всего происходят ситуации с непопаданием в окно доставки?
2. В какое окно доставки чаще всего происходят ситуации с непопаданием в окно доставки?
3. Из каких ретейлов чаще всего заказы не попадают в окно доставки?
4. Из каких магазинов чаще всего заказы не попадают в окно доставки?
5. Есть ли связь, между количеством едениц заказа и непопаданием в окно доставки? Например, заказывают более 50 товаров и сотрудник не успевает собрать их.

## 3. Изменения ежедневной выручки в течение 2019 года
Взяли 2019 год, так как за 2018 год есть данные начиная только с августа.
"""

# Создадим таблицу в которой будут дни и месяцы заказа, а также итоговая стоимость заказа. 
ordesr_2019 = orders[orders['created_at'].dt.year == 2019]
revenue_byday_month = ordesr_2019.groupby([ordesr_2019['created_at'].dt.day,
                                        ordesr_2019['created_at'].dt.month])['total_cost'].sum()
revenue_byday_month.index.names = ['day','month']
revenue_byday_month = revenue_byday_month.reset_index() 
revenue_byday_month

# Нарисуем Boxplot для анализа ежедневной выручки компании по месяцам

plt.figure(figsize=(16, 8))  
plt.title('Распределение суммы заказов по месяцам') 
plt.grid()
sb.boxplot(x='month',
            y='total_cost',
            data=revenue_byday_month, 
            color='y')
plt.ylabel('Выручка в день') 
plt.xlabel('Месяц') 
plt.show()

"""#### Как видим из графика, медиана ежедневной выручки растет из месяца в месяц. Стоит обратить внимение на ноябрь, видимо была сильная маркетинговая активность, которая побудила клиентов к заказам. Если бы мы знали стоимость этой маркетинговой активности, то могли бы посчитать ROMI.

## 4. Нагрузка по окну доставки для различных временных зон

Для удобства работы с различными временными зонами можем воспользоваться функцией, которая будет предлагать на выбор временную зону для анализа. В дальнейшем при увеличении временных зон, такая функция будет более простая в эксплуатации.
"""

def heatmap_weekdhour():
    time = input('Выберете временную зону:' '\n' '1 - Europe/Moscow' '\n' '2 - Europe/Kaliningrad' '\n' 
      '3 - Asia/Yekaterinburg' '\n' '4 - Europe/Samara' '\n' '5 - Asia/Omsk' '\n')
    
    orders_and_delivery = orders.merge(delivery_windows, left_on = 'delivery_window_id', right_on = 'id')
    orders_and_delivery_shipped = orders_and_delivery.loc[orders_and_delivery['state'] == 'shipped']
    orders_and_delivery_shipped['hour'] =  orders_and_delivery_shipped['starts_at'].dt.hour
    orders_and_delivery_shipped['dayofweek'] = orders_and_delivery_shipped['starts_at'].dt.dayofweek
    if time == '1':
        orders_and_delivery_shipped = orders_and_delivery_shipped.loc[orders_and_delivery_shipped['time_zone'] == 'Europe/Moscow']
    elif time =='2':
        orders_and_delivery_shipped = orders_and_delivery_shipped.loc[orders_and_delivery_shipped['time_zone'] == 'Europe/Kaliningrad']
    elif time =='3':
        orders_and_delivery_shipped = orders_and_delivery_shipped.loc[orders_and_delivery_shipped['time_zone'] == 'Asia/Yekaterinburg']
    elif time =='4':
        orders_and_delivery_shipped = orders_and_delivery_shipped.loc[orders_and_delivery_shipped['time_zone'] == 'Europe/Samara']
    elif time =='5':
        orders_and_delivery_shipped = orders_and_delivery_shipped.loc[orders_and_delivery_shipped['time_zone'] == 'Asia/Omsk']
    else: 
        return'Вы ввели неправильную временную зону, перезапустите функцию и попробуйте еще раз'
    delivery_shipped_hourday = orders_and_delivery_shipped.groupby(['hour', 'dayofweek'])['state'].count()
    delivery_shipped_hourday = delivery_shipped_hourday.reset_index()
    heat_weekdhour = delivery_shipped_hourday.pivot(index="dayofweek", columns="hour", values="state")
    heat_weekdhour.index = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресение']
    heat_weekdhour.fillna(0, inplace=True)
    plt.figure(figsize=(20,8))
    sb.heatmap(heat_weekdhour, annot=True, cmap="YlGnBu", fmt='g')
    plt.title("Нагрузка окон доставки, по часам и дням недели")
    plt.ylabel("День недели")
    plt.xlabel("Час")
    plt.show()

# Вызовем функцию, для анализа нагрузки окна доставки в течение дня.
heatmap_weekdhour()

"""#### Проанализировав тепловую карту по нагрузке окон доставки, можно сделать следующие выводы:
1. В Московской временной зоне доставку заказывают с 5 утра и до 21 часа. (В таблице показаны "starts_at", поэтому к конечному времени прибавляем 1 час). Нагрузка на вечерние окна доставки в 18, 19 и 20 часов, меньше по сравнению с дневной.
2. В Калининградской временной зоне в целом мало заказов. Доставку заказывают на период с 7 до 20 часов.
3. По времени Екатеринбурга, слоты доставки с 4 до 18 часов. Пиковая нагрузка приходится на обеденное время 13:00.
4. Жители Самарской временной зоны предпочитают делать заказы на период с 5 до 19 часов. Стоит отметить, что на слот доставки начинающийся в 6 утра довольно большая нагрузка, по сравнению с другими утренними и даже обеденными часами.
5. По Омскому времени, доставку заказывают с 3 до 15 часов. Это самые ранние заказы из исследуемых данных. Пиковая нагрузка происходит на 13:00. Интересно что в выходные дни есть увеличение количества заказов на 5 утра, по сравнению с другими днями недели.

## 5. Товары из каких ретейлов чаще всего подвергаются возврату или отмене
"""

# Соберем таблицу в которой будут данные по заказам товары в которых были заменены, ретейлам, городам и магазинам.

replacements_city_store = orders.merge(stores, left_on='store_id', right_on='id').merge(replacements, left_on='id_x', right_on='order_id')
replacements_city_store = replacements_city_store.loc[:, ['retailer_id', 'order_id', 'city', 'store_id']]
replacements_city_store.head()

# Сгруппируем данные по количеству замененных товаров у различных ретейлов. Предварительно удалив дубликаты заказов.
replacements_retailer = replacements_city_store.drop_duplicates(subset = ['order_id']).reset_index(drop = True).groupby('retailer_id')['order_id'].count()
replacements_retailer

"""Видим интересный результат, что в абсолютном значении наибольшее количество замененных товаров у ретейла ID=1, а наименьшее у ID=16. Посмотрим на относительный результат."""

percent_replacements_retailer = ((replacements_retailer) / quantity_and_weight_shipped.groupby('retailer_id')['shipped_at'].count())
print('Доля заказов которые подвергались замене товаров, по ретейлам:',
      '\n' 'retailer ID=1 : {:.2%}'.format(percent_replacements_retailer[1]),
      '\n' 'retailer ID=8 : {:.2%}'.format(percent_replacements_retailer[8]),
      '\n' 'retailer ID=15 : {:.2%}'.format(percent_replacements_retailer[15]),
      '\n' 'retailer ID=16 : {:.2%}'.format(percent_replacements_retailer[16]),
     '\n' 'Среднее значение : {:.2%}'.format(percent_replacements_retailer.mean()))

"""#### Из отправленных заказов в среднем 63% заказов подвергались замене товаров."""

# Соберем таблицу в которой будут данные по заказам товары в которых были отменены, ретейлам, городам и магазинам.

cancellations_city_store = orders.merge(stores, left_on='store_id', right_on='id').merge(cancellations, left_on='id_x', right_on='order_id')
cancellations_city_store = cancellations_city_store.loc[:, ['retailer_id', 'order_id', 'city', 'store_id']]

# Сгруппируем данные по количеству отмененных товаров у различных ретейлов. Предварительно удалив дубликаты заказов.
cancellations_retailer = cancellations_city_store.drop_duplicates(subset = ['order_id']).reset_index(drop = True).groupby('retailer_id')['order_id'].count()
cancellations_retailer

percent_cancellations_retailer = ((cancellations_retailer) / quantity_and_weight_shipped.groupby('retailer_id')['shipped_at'].count())
print('Доля заказов которые подвергались отмене товаров, по ретейлам:',
      '\n' 'retailer ID=1 : {:.2%}'.format(percent_cancellations_retailer[1]),
      '\n' 'retailer ID=8 : {:.2%}'.format(percent_cancellations_retailer[8]),
      '\n' 'retailer ID=15 : {:.2%}'.format(percent_cancellations_retailer[15]),
      '\n' 'retailer ID=16 : {:.2%}'.format(percent_cancellations_retailer[16]),
     '\n' 'Среднее значение : {:.2%}'.format(percent_cancellations_retailer.mean()))

"""#### Из отправленных заказов в среднем в 62% заказов были отменены некоторые товары.

### Что еще можно покопать в данном направлении:
1. В каких городах чаще всего происходят какие-либо действия с товарами?
2. В каких конкретных магазинах происходит больше всего изменений в структуре заказа?
3. Какие товары чаще всего подвергаются отмене или замене?

# Выводы и рекомендации по заданию №1

На основе тех данных которые получили можем рекомендовать следующие действия:
1. Проверить где происходят проблемы при заполнение таблицы с данными. Так как существует большое количестов пропущенных значений или нереальных, которые могут влиять на качество работы с данными.
2. Каждый четвертый заказ не попадает в окно доставки. Стоит уделить этому аспекту более пристольное внимание, так как это может повлиять на лояльность клиентов. Нужно пообщаться с руководством и сотрудниками для понимания причин таких событий.
3. В ноябре 2019 года, видимо была сильная маркетинговая активность, которая побудила клиентов к заказам. Если бы мы знали стоимость этой маркетинговой активности, то могли бы посчитать ROMI и говорить о выгоде такой активности и дать рекомендации о будущих её проведениях.
4. По времени Екатеринбурга пиковая нагрузка приходится на обеденное время 13:00. Стоит рекомендовать сотрудникам заранее собирать заказы для этого периода времени.
5. У жителей Самарской временной в выходные дни есть увеличение количества заказов на 5 утра, по сравнению с другими днями недели. Стоит уделить внимание этому аспекту и предупредить сотрудников.
6. Более 60% всех отправленных заказов подвергаются изменениям товаров, будь то замена или отказ. Стоит уделить внимание этому аспекту бизнеса и продумать как избежать этого в будущем. Например: отбирать товары из магазина с утра на весь день в отдельное хранилище, чтобы не было случаев, когда товар заказали, а он кончился на полке.
"""

