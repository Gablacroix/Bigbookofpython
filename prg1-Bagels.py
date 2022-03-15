# Напишите здесь свой код :-)
import random

NUM_DIGITS = 3  # (!) Try setting this to 1 or 10.
MAX_GUESSES = 10  # (!) Try setting this to 1 or 100.


def main():
    print(
        """Бейглс , дедуктивная логичистка игра.
От Gabriel Lacroix
Я думаю о {}-значном числе с неповторяющимся цифрами.
Попытайтесь его разгадать
Когда я говорю:     Я подразумеваю:
  Pico              Одна цифра верна но не в том месте
  Fermi             Одна цифра верна и в нужном месте
  Bagels            Все цифры не верны

Для примера  Если секретное число 248 и Вы  предпологаете 843,
подсказки будут Fermi Pico""".format(
            NUM_DIGITS
        )
    )
    while True:  # main circle
        # переменная в которой хранится секретное число
        secretNum = getSecretNum()
        print("Я загадал число.")
        print("У тебя есть {} попыток угадать его.".format(MAX_GUESSES))

        numGuesses = 1
        while numGuesses <= MAX_GUESSES:
            guess = ""
            # прододжаем итерации для получения правильной догадки
            while len(guess) != NUM_DIGITS or not guess.isdecimal():
                print("Предположение №{}: ".format(numGuesses))
                guess = input("> ")
            clues = getClues(guess, secretNum)
            print(clues)
            numGuesses += 1

            if guess == secretNum:
                break  # They're correct, so break out of this loop.
            if numGuesses > MAX_GUESSES:
                print("Предположения закончились")
                print("Правильный ответ {}.".format(secretNum))
        # Спрашиваем о доп. игре
        print("Хочешь сыграть еще ? (yes or no)")
        if not input("> ").lower().startswitch("y"):
            break
    print("Спасибо за игру!")

def getSecretNum():
    # возвращаем строку
    numbers = list("0123456789")  # создаем список 0-9
    random.shuffle(numbers)  # Перемешиваем
    # берем первые NUM_DIGITS цифр из списка
    secretNum = ""
    for i in range(NUM_DIGITS):
        secretNum += str(numbers[i])
    return secretNum

def getClues(guess, secretNum):
    # Возвращает строку с подсказками
    if guess == secretNum:
        return "Вы выйграли"
    clues = []

    for i in range(len(guess)):
        if guess[i] == secretNum[i]:
            # Правильная цифра в правильном месте
            clues.append("Fermi")
        elif guess[i] in secretNum:
            # Правильная цифра в неправильном месте
            clues.append("Pico")
    if len(clues) == 0:
        return "Bagels"  # правильных нет вообще
    else:
        # сортируем порядок в алфавитном порядке
        clues.sort()
        # склеиваем список в одно строковое
    return " ".join(clues)

if __name__ == "__main__":
    main()
