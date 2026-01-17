class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Seat:
    def __init__(self, seat_id, row, number):
        self.seat_id = seat_id      # ID места
        self.row = row              # Ряд
        self.number = number        # Номер в ряду
        self.status = "свободно"    # свободно/забронировано/продано
        self.current_user = None    # Кто занимает место

    def __str__(self):
        if self.current_user:
            user_info = f"({self.current_user})"
        else:
            user_info = ""
        return f"Ряд {self.row}, Место {self.number}: {self.status}{user_info}"


class EventSession:
    def __init__(self, session_id, time):
        self.session_id = session_id
        self.time = time
        self.seats = {}  # Словарь мест

    def add_seat(self, seat):
        self.seats[seat.seat_id] = seat

    def get_seat(self, seat_id):
        return self.seats.get(seat_id)

    def show_seats(self):
        print(f"\nСеанс {self.session_id} ({self.time})")
        for seat in self.seats.values():
            print(seat)


class BookingCommand:
    def execute(self, session, seat_id, user):
        pass

    def undo(self, session):
        pass


class ReserveSeatCommand(BookingCommand):
    def execute(self, session, seat_id, user):
        seat = session.get_seat(seat_id)
        if not seat:
            print(f"Место {seat_id} не найдено")
            return False

        if seat.status == "свободно":
            seat.status = "забронировано"
            seat.current_user = user
            print(f"{user.name} забронировал место {seat_id}")
            return True
        else:
            print(f"Место {seat_id} занято")
            return False

    def undo(self, session):
        print("Отмена бронирования")


class CancelReservationCommand(BookingCommand):
    def execute(self, session, seat_id, user):
        seat = session.get_seat(seat_id)
        if not seat:
            print(f"Место {seat_id} не найдено")
            return False

        if seat.status == "забронировано" and seat.current_user == user:
            seat.status = "свободно"
            seat.current_user = None
            print(f"{user.name} отменил бронь места {seat_id}")
            return True
        else:
            print(f"Нельзя отменить бронирование")
            return False

    def undo(self, session):
        print("Отмена отмены брони")


class PurchaseTicketCommand(BookingCommand):
    def execute(self, session, seat_id, user):
        seat = session.get_seat(seat_id)
        if not seat:
            print(f"Место {seat_id} не найдено")
            return False

        if seat.status == "забронировано" and seat.current_user == user:
            seat.status = "продано"
            print(f"{user.name} купил билет на место {seat_id}")
            return True
        else:
            print(f"Нельзя купить это место")
            return False

    def undo(self, session):
        print("Отмена покупки")


class BookingProcessor:
    def __init__(self):
        self.commands = []  # Список выполненных команд

    def execute_command(self, command, session, seat_id, user):
        print(f"\nВыполняем команду")
        if command.execute(session, seat_id, user):
            self.commands.append((command, seat_id, user))
            session.show_seats()
            return True
        return False

    def undo_last(self, session):
        if self.commands:
            command, seat_id, user = self.commands.pop()
            print(f"\nОтменяем последнюю команду")
            command.undo(session)
            session.show_seats()


def main():
    #Создаем пользователей
    user1 = User("User1", "Матвик")
    user2 = User("User2", "Толян")
    print(f"Созданы: {user1} и {user2}")

    #Добавляем места в зал
    seats_data = [
        ("A1", 1, 1), ("A2", 1, 2), ("A3", 1, 3),
        ("A4", 1, 4), ("A5", 1, 5)
    ]

    #Создаем сеанс
    session = EventSession("S_test", "2:00")

    for seat_id, row, number in seats_data:
        seat = Seat(seat_id, row, number)
        session.add_seat(seat)

    #Начальное состояние
    session.show_seats()

    #Процессор операций
    processor = BookingProcessor()

    #Проверка брони
    reserve_cmd = ReserveSeatCommand()
    processor.execute_command(reserve_cmd, session, "A1", user1)

    processor.execute_command(reserve_cmd, session, "A1", user2)

    processor.execute_command(reserve_cmd, session, "A2", user2)

    #Проверкка покупок
    purchase_cmd = PurchaseTicketCommand()
    processor.execute_command(purchase_cmd, session, "A2", user2)

    processor.execute_command(purchase_cmd, session, "A1", user2)

    processor.execute_command(purchase_cmd, session, "A1", user1)

    #Проверка отмены брони
    cancel_cmd = CancelReservationCommand()
    processor.execute_command(cancel_cmd, session, "A3", user1)

    processor.execute_command(reserve_cmd, session, "A4", user2)

    processor.execute_command(cancel_cmd, session, "A4", user2)


if __name__ == "__main__":
    main()
