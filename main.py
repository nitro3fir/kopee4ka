import json
import datetime
from calendar import monthrange

MONTHS_NUM_TO_STR_ROD = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
MONTHS_NUM_TO_STR_IM = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
CALCULATION_TYPE = ["накопительный", "амортизирующий"]

class User:
	def __init__(self, date):
		self.__directory = ["main"]
		self.__date = date
		self.__calculation_type = 0
		try:
			with open("profile.json", "r") as readfile:
				data = json.loads(readfile.read())
			self.__income, self.__predicted_expenses, self.__calculation_type = data.get(str(self.__date.year)).get(str(self.__date.month))
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

	def get_calculation_type(self):
		return self.__calculation_type

	def get_income(self):
		return self.__income

	def get_predicted_expenses(self):
		return self.__predicted_expenses

	def get_notes(self):
		return self.__notes

	def get_date(self):
		return self.__date

	def get_directory(self):
		return self.__directory

	def get_month_len(self):
		return len(self.__notes)

	def get_total_expenses(self):
		return sum(self.__notes)

	def set_calculation_type(self, type):
		try:
			if int(type) in (0, 1):
				self.__calculation_type = int(type)
			else:
				return "type not 0 or 1"
		except Exception as e:
			return e

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
			profile_data[str(self.__date.year)][str(self.__date.month)] = [self.__income, self.__predicted_expenses, self.__calculation_type]
			if not str(self.__date.year) in notes_data.keys():
				notes_data[str(self.__date.year)] = {}
			notes_data[str(self.__date.year)][str(self.__date.month)] = self.__notes
		except Exception as e:
			profile_data = {str(self.__date.year):{str(self.__date.month):[self.__income, self.__predicted_expenses, self.__calculation_type]}}
			notes_data = {str(self.__date.year):{str(self.__date.month):self.__notes}}
		with open('profile.json', 'w') as f:
			json.dump(profile_data, f, ensure_ascii=False, indent=4)
		with open('notes.json', 'w') as f: 
			json.dump(notes_data, f, ensure_ascii=False, indent=4)

def saving_type(report, notes, date, predicted_expenses):
	daily_rate = round(predicted_expenses/len(notes), 2)
	balance = 0
	for day_num in range(date.day):
		daily_rate_copy = daily_rate
		balance = round(balance+daily_rate, 2)
		note = notes[day_num]
		if note > balance:
			daily_rate = round(daily_rate - (note-balance)/(len(notes)-day_num), 2)
			balance = 0
		else:
			balance = round(balance-note, 2)
		report.append(f"{day_num+1} {MONTHS_NUM_TO_STR_ROD[date.month-1]}:\nРасходы - {notes[day_num]}р\nБаланс на конец дня - {balance}р\nЛимит на начало дня - {daily_rate_copy}р\n")

def amortizing_type(report, notes, date, predicted_expenses):
	daily_rate = round(predicted_expenses/len(notes), 2)
	for day_num in range(date.day):
		daily_rate_copy = daily_rate
		note = notes[day_num]
		if note > daily_rate:
			daily_rate = round(daily_rate - (note-daily_rate)/len(notes)-day_num, 2)
		else:
			daily_rate = round(daily_rate + (daily_rate-note)/len(notes)-day_num, 2)
		report.append(f"{day_num+1} {MONTHS_NUM_TO_STR_ROD[date.month-1]}:\nРасходы - {notes[day_num]}р\nЛимит на начало дня - {daily_rate_copy}р")

def answer(user):
	if user.get_directory()[-1] == "main":
		return "Введите '1', чтобы перейти в месячные траты\nВведите '2', чтобы ввести расход за день"

	elif user.get_directory()[-1] == "profile":
		report = []
		report.append(f"Тип расчета: {CALCULATION_TYPE[user.get_calculation_type()]}")
		report.append(f"Траты за {MONTHS_NUM_TO_STR_IM[user.get_date().month-1]} {user.get_date().year} года по дням\n")
		if user.get_calculation_type() == 0:
			saving_type(report, user.get_notes(), user.get_date(), user.get_predicted_expenses())
		elif user.get_calculation_type() == 1:
			amortizing_type(report, user.get_notes(), user.get_date(), user.get_predicted_expenses())
		report.append(f"Доход: {user.get_income()}")
		report.append(f"Планируемый расход: {user.get_predicted_expenses()}")
		report.append(f"Уже потрачено: {user.get_total_expenses()}")
		report.append("Введите 'изм доход *значение*', чтобы изменить доход за месяц")
		report.append("Введите 'изм расход *значение*', чтобы изменить целевой расход за месяц")
		report.append("Введите 'изм расчет *0 - накопительный, 1 - амортизирующий*', чтобы изменить тип расчета")
		report.append("Введите 'расчет', чтобы посмотреть описание типов расчета")
		report.append("Введите 'назад', чтобы выйти в главное меню\n\n")
		return "\n".join(report)

	elif user.get_directory()[-1] == "result":
		return f"Введите трату за {user.get_date().day} {MONTHS_NUM_TO_STR_ROD[user.get_date().month-1]} {user.get_date().year} года (Пример: 234.54)\nИли введите 'назад' чтобы вернутся в меню\n\n"

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

		elif user_answer[0:10] == "изм расчет":
			error = user.set_calculation_type(user_answer[11:])
			if error:
				print("Ошибка: не удалось определить тип")
			else:
				print("Тип расчета изменен")

		elif user_answer[0:6] == "расчет":
			print("Накопительный - излишки при тратах будут концентрироваться в балансе, избытки будут распределяться в оставшихся днях месяца")
			print("Амортизирующий - излишки и избытки при тратах будут распределяться в оставшихся днях месяца")

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
	user_answer = None
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