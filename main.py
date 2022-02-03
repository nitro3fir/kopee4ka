import json
import datetime
from calendar import monthrange

MONTHS_NUM_TO_STR_ROD = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
MONTHS_NUM_TO_STR_IM = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

class User:
	def __init__(self, date):
		self.__directory = ["main"]
		self.__date = date
		try:
			with open("profile.json", "r") as readfile:
				data = json.loads(readfile.read())
			self.__income, self.__predicted_expenses = data.get(str(self.__date.year)).get(str(self.__date.month))
			with open("notes.json") as readfile:
				data = json.loads(readfile.read())
			self.__notes = data.get(str(self.__date.year)).get(str(self.__date.month))
		except Exception as e:
			self.__income = 0
			self.__predicted_expenses = 0
			self.__notes = [0 for i in range(monthrange(self.__date.year, self.__date.month)[1])]

	def add_note(self, note, date):
		try:
			self.__notes[date.day-1] = round(float(note), 2)
		except Exception as e:
			return e

	def get_income(self):
		return self.__income

	def get_total_expenses(self):
		return sum(self.__notes)

	def get_daily_rate(self):
		return round(self.__predicted_expenses/len(self.__notes), 2)

	def get_predicted_expenses(self):
		return self.__predicted_expenses

	def get_note_by_day(self, day):
		return self.__notes[day]

	def get_date(self):
		return self.__date

	def get_directory(self):
		return self.__directory

	def get_month_len(self):
		return len(self.__notes)

	def set_income(self, note):
		try:
			self.__income = round(float(note), 2)
		except Exception as e:
			return e

	def set_predicted_expenses(self, note):
		try:
			self.__predicted_expenses = round(float(note), 2)
		except Exception as e:
			return e

	def to_profile(self):
		self.__directory.append("profile")
		
	def get_back(self):
		if len(self.__directory) > 1:
			self.__directory = self.__directory[0:-1]

	def to_result(self):
		self.__directory.append("result")

	def __del__(self):
		try:
			with open("profile.json", "r") as readfile:
				profile_data = json.loads(readfile.read())
			with open("notes.json") as readfile:
				notes_data = json.loads(readfile.read())
			if not str(self.__date.year) in profile_data.keys():
				profile_data[str(self.__date.year)] = {}
			profile_data[str(self.__date.year)][str(self.__date.month)] = [self.__income, self.__predicted_expenses]
			if not str(self.__date.year) in notes_data.keys():
				notes_data[str(self.__date.year)] = {}
			notes_data[str(self.__date.year)][str(self.__date.month)] = self.__notes
		except Exception as e:
			profile_data = {str(self.__date.year):{str(self.__date.month):[self.__income, self.__predicted_expenses]}}
			notes_data = {str(self.__date.year):{str(self.__date.month):self.__notes}}
		with open('profile.json', 'w') as f:
			json.dump(profile_data, f, ensure_ascii=False, indent=4)
		with open('notes.json', 'w') as f: 
			json.dump(notes_data, f, ensure_ascii=False, indent=4)

def answer(user):
	if user.get_directory()[-1] == "main":
		return "Введите '1', чтобы перейти в месячные траты\nВведите '2', чтобы ввести расход за день"
		return "1 - Перейти в профиль\n2 - Ввести результат за день\n\n"

	elif user.get_directory()[-1] == "profile":
		notes = []
		daily_rate = user.get_daily_rate()
		balance = 0
		for day_num in range(user.get_date().day):
			daily_rate_copy = daily_rate
			balance = round(balance+daily_rate, 2)
			note = user.get_note_by_day(day_num)
			if note > balance:
				daily_rate = round(daily_rate - note/(user.get_month_len()-day_num), 2)
			else:
				balance = round(balance-note, 2)
			notes.append(f"{day_num+1} {MONTHS_NUM_TO_STR_ROD[user.get_date().month-1]}: расходы - {user.get_note_by_day(day_num)}р,  баланс - {balance}р, лимит на день - {daily_rate_copy}р")
		notes.append(f"Доход: {user.get_income()}")
		notes.append(f"Планируемый расход: {user.get_predicted_expenses()}")
		notes.append(f"Уже потрачено: {user.get_total_expenses()}")
		notes.append(f"Текущий баланс: {balance}")
		return "\n".join([f"Траты за {MONTHS_NUM_TO_STR_IM[user.get_date().month-1]} по дням"]+notes+["Введите 'изм доход *значение*', чтобы изменить доход за месяц\nВведите 'изм расход *значение*', чтобы изменить целевой расход за месяц\nВведите 'назад', чтобы выйти в главное меню\n\n"])

	elif user.get_directory()[-1] == "result":
		return f"Введите трату за {user.get_date().day} {MONTHS_NUM_TO_STR_ROD[user.get_date().month-1]} (Пример: 234.54)\nИли введите 'назад' чтобы вернутся в меню\n\n"

def processing(user, user_answer):
	if user.get_directory()[-1] == "main":
		if user_answer == "1":
			user.to_profile()
		elif user_answer == "2":
			user.to_result()

	elif user.get_directory()[-1] == "profile":
		if user_answer[0:9] == "изм доход":
			error = user.set_income(user_answer[10:])
			if error:
				print("Ошибка: неверный формат записи")
			else:
				print("Доход изменен")

		elif user_answer[0:10] == "изм расход":
			error = user.set_predicted_expenses(user_answer[11:])
			if error:
				print("Ошибка: неверный формат записи")
			else:
				print("Расход изменен")

		elif user_answer == "назад":
			user.get_back()

	elif user.get_directory()[-1] == "result":
		if user_answer == "назад":
			user.get_back()
		else:
			error = user.add_note(user_answer, user.get_date())
			if error:
				print("Ошибка: неверный формат записи", error)
			else:
				print("Запись сохранена")

def main_loop():
	user_answer = ""
	user = User(datetime.date.today())
	print("Копее4ка\nЖиви на широкую ногу и не в кредит\nДля выхода из программы ввести 'q' (иначе введенные данные не сохранятся)\n\nВведите '1', чтобы перейти в месячные траты\nВведите '2', чтобы ввести расход за день\n")
	while user_answer != "q":
		print("Ввод: ", end="")
		user_answer = input()
		print("\n")
		processing(user, user_answer)
		print(answer(user))
	del user

if __name__ == "__main__":
	main_loop()