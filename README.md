# Возможности пользователя

Бот работает на inline-кнопках. Все, что ниже называется командой подразумевает под собой наличие именно inline-кнопки. Все таблицы отрисовываются в вертикальном формате с целью повышения читаемости

Под "есть коммиты" подразумевается статус задачи submitted. Под "сдано" подразумевается passed

## Старт бота

1. При старте пользователь видит приветственное сообщение и команду "привязать GitHub" со ссылкой на привязку своего GitHub-аккаунта

## Общий функционал

1. Всегда есть возможность разлогиниться
2. Если можно разлогиниться, то и заново залогиниться тоже можно
3. Можно привязать новые аккаунты
4. Можно менять привязанные аккаунты между собой
5. Если пользователь уже привязал GitHub, то он может выбрать свою роль. При выборе роли учителя производится доп проверка (может ли пользователь логиниться под такой ролью), при выборе администратора - проверка по айди в телеграмме

6. Пользователь умеет выключать уведомления, которые описаны в его возможностях

## Студент

1. Выбрать курс, в котором сидит (опционально, последующие команды доступны и без этого)

2. Кнопка "сменить курс" для смены выбранного курса

3. Сводка всех активных заданий в виде таблицы:

   * Курс (если выбран)
   * Задание
   * Статус задания (Сдано/Не сдано)
   * Дедлайн

4. Сводка всех просроченных заданий в виде такой же таблицы.

5. Сводка по оценкам за сданные задачи:

    * Курс (если выбран)
    * Задание
    * Статус (оценено/не оценено)
    * Оценка (если есть)

6. Сводка по конкретной задаче (нажимаешь на кнопку сводки, внутри выбираешь курс и задачу/только задачу в зависимости от того, выбран ли курс):

   * Задача
   * Статус (не сдано/есть коммиты/сдано)
   * Балл (либо "не проверена", если задача сдана)

7. Получение уведомлений. По умолчанию:

    * Дедлайн через 24 часа
    * Дедлайн через 3 часа
    * Дедлайн наступил

8. Открыть список настроек с моментами, когда студент хочет получать уведомления (тоже в виде inline-кнопок). По нажатии на такую кнопку пользователь видит возможность изменить время или же удалить настройку. Кроме кнопок с введенными настройками, студент видит кнопку "вернуть настройки по умолчанию" и "добавить новое время". После чего видит сообщение с просьбой ввести целое число часов, за которое его нужно предупреждать о дедлайне.

9. Отправить обратную связь по курсу:

   Кнопка "обратная связь" -> выбрать курс -> анонимно/не анонимно -> ввод сообщения

## Преподаватель

1. Выбрать курс, в котором сидит (опционально, последующие команды доступны и без этого)

2. Кнопка "сменить курс" для смены выбранного курса

3. Выбрать задачу, которую смотрим (доступно при выбранном курсе)

4. Кнопка "сменить задачу" для смены задачи

5. Просмотр сводки по всем студентам курса (только при отсутствии выбранной задачи):

   * ФИО студента
   * Юзернейм в GitHub
   * Количество просрочек
   * Средний балл среди оцененных задач (просроченная задача считается оцененной нулем)
   * Дата последнего коммита


6. Просмотр отчёта по отдельному заданию:

   * ФИО студента
   * Юзернейм в GitHub
   * Статус задачи (сдано/не сдано)

7. Список юзернеймов студентов, которые залогинились в Classroom, но не появились в боте


8. Просмотр всех дедлайнов курса:

    * Задание
    * Дедлайн
    * Количество сданных работ
    * Количество не сданных работ

9. Сводка по задачам, которые необходимо оценить (дедлайн прошел):

    * Задание
    * Дедлайн
    * Количество несданных работ
    * Количество оцененных работ
    * Количество работ к оценке

10. Получение уведомлений:

   * Когда дедлайн прошел, получить количество студентов, не сдавших задание. Под ним список из ФИО и Юзернейма

11. Сводка по сданным задачам с ручной проверкой:

   * Курс (если не выбран)
   * Задача
   * ФИО студента
   * Юзернейм студента
   * Дата сдачи 
   * Дата дедлайна задачи


12. Делать объявления для студентов определенного курса.

13. Добавить ассистента по @username

14. Удалить ассистента по @username

15. Принудительное обновление БД.

   * Поскольку дорого при каждом запросе к боту обращаться в API, обновление наших локальных баз данных мы будем делать раз в 8 часов. Если же преподаватель обновил дд/знает, что прошла массовая проверка ручных заданий, то он может принудительно запустить обновление БД. Не чаще 5 раз в день (остальное по договоренности с админом бота)

## Ассистент:

   Роль обладает всеми возможностями преподавателя, кроме пунктов 12-15

## Администратор

1. Управление ролями пользователей:

   * Возможность дать роль "Учитель" по @username
   * Возможность отнять роль "Учитель" по @username
   * Возможность забанить по @username
   * Разбан пользователя по @username

2. Логирование:

    * Выгрузить количество ошибок бота за день
    * Выгрузить дату последнего успешного обращения к GitHub
    * Выгрузить дату последнего обращения к GitHub с ошибкой. Вывести статус обращения

# Директории

Ясно, что в каждой папке есть свой init. Они тут не прописаны, поскольку их содержание предельно ясное

## .env

```
TEST_DATABASE=postgresql+asyncpg://ababa:ababa@localhost/testdb
DATABASE_URL=postgresql+asyncpg://ababa:ababa@db:5432/classroom_bot_db
GITHUB_CLASSROOM_TOKEN=ababababab
BOT_TOKEN=ababababab
GITHUB_CLIENT_ID=ababababab
GITHUB_CLIENT_SECRET=ababababab
GITHUB_REDIRECT_URI=ababababab
GITHUB_ORG=ababababab
POSTGRES_USER=ababa
POSTGRES_PASSWORD=ababa
POSTGRES_DB=classroom_bot_db
```

## models

### db.py - таблицы

Реализуются БД на основе SQLAlchemy. Наглядно на схеме 
![](DB.png)

В файле необходимо прописать описание всех таблиц при помощи SQLAlchemy 

### gh_client.py

* Клиент, который вытаскивает из .env токен, и через него мы можем ходить к гитхабу. Клиент имеет класс GitHubClassroomClient

## commands

Тут важно понимать, что в каждом сценарии возможны ошибки. Обязательно надо прописать логику их логирования в бд. Поэтому в каждую функцию аргументом передается сессия (чтобы в случае чего записать в БД ошибку)

### common_commands.py

```python
async def create_user(telegram_id: int, telegram_username: str, session: AsyncSession) -> None:
    """"Создать профиль юзера при старте"""
    

async def create_permission_student(telegram_id: int, session: AsyncSession) -> None:
    """Выдать базовую роль 'student'"""
    
    
async def set_active_role(telegram_id: int, role: str, session: AsyncSession) -> None:
    """Установить активную роль пользователя: 'student', 'teacher', 'assistant', 'admin'. С проверкой на доступность роли"""
    

async def toggle_global_notifications(telegram_id: int, session: AsyncSession) -> None:
    """Глобально сменить рычажок уведомлений по дд для пользователя."""

async def change_git_account(telegram_id: int, github_login: str, session: AsyncSession) -> None:
   """Сменить гитхаб-аккаунт на другой залогиненный"""


async def enter_name(telegram_id: int, full_name: str, session: AsyncSession) -> None:
    """Добавить в бд полное имя пользователся"""
```

### student_commands.py


```python
async def set_student_active_course(telegram_id: int, course_id: Optional[int], session: AsyncSession) -> None:
    """Установить/или сбросить активный курс студента."""


async def get_student_notification_rules(telegram_id: int, session: AsyncSession) -> Sequence[int]:
    """Получить список времен уведомлений студента."""
    

async def add_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Добавить новое правило уведомлений."""
    

async def remove_student_notification_rule(telegram_id: int, hours_before: int, session: AsyncSession) -> None:
    """Удалить правило уведомлений."""
    

async def reset_student_notification_rules_to_default(telegram_id: int, session: AsyncSession) -> None:
    """Сбросить правила уведомлений к дефолтным."""

async def get_student_active_assignments_summary(
    telegram_id: int,
    course_id: Optional[int] = None, session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех активных заданий студента. Сортировка по дд"""
    

async def get_student_overdue_assignments_summary(
    telegram_id: int,
    course_id: Optional[int] = None,
    now: Optional[datetime] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех просроченных заданий студента. Сортировка по дд"""
    

async def get_student_grades_summary(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка по оценкам за сданные задачи — оценено/не оценено + баллы. Сортировка по дд"""
    

async def get_student_assignment_details(
    telegram_id: int,
    assignment_id: int,
    session: AsyncSession
) -> Mapping[str, Any]:
    """Подробности по конкретной задаче: статус, балл, дата сдачи."""


async def submit_course_feedback(
    telegram_id: int,
    course_id: int,
    message: str,
    anonymous: bool,
    session: AsyncSession
) -> None:
    """Отправить анонимную или неанонимную обратную связь по курсу."""

async def find_students_courses(
        student_telegram_id: int,
        session: AsyncSession
) -> list[tuple[Any, ...]]:
    """Вытягивает по айди студента курсы, где он является учеником (есть сабмиты)"""

```

### teacher_and_assistant_commands.py

```python
async def set_teacher_active_course(telegram_id: int, course_id: Optional[int], session: AsyncSession) -> None:
    """Установить/сбросить активный курс пользователя."""
    

async def set_teacher_active_assignment(telegram_id: int, assignment_id: Optional[int], session: AsyncSession) -> None:
    """Установить/сбросить активное задание для пользователя."""


async def get_course_students_overview(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка: ФИО, Курс, GitHub, просрочки, средний балл, дата последнего коммита. Сортировка по ФИО и названию курса (в соответствующем порядке)"""
    

async def get_assignment_students_status(
    telegram_id: int,
    assignment_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка по отдельному заданию: ФИО, GitHub, статус. Сортировка по статусу и ФИО"""
    

async def get_classroom_users_without_bot_accounts(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[str]:
    """GitHub-логины студентов, которых нет в боте. Таковыми считаем тех, кто хоть что-то сдавал по некоторому заданию"""
    

async def get_course_deadlines_overview(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка всех дедлайнов. Сортировка по дд"""
    

async def get_tasks_to_grade_summary(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка по задачам, которые нужно оценить. Сортировка по дд и названию курса"""
    

async def get_manual_check_submissions_summary(
    telegram_id: int,
    course_id: Optional[int] = None,
    session: AsyncSession
) -> Sequence[Mapping[str, Any]]:
    """Сводка по ручной проверке: ФИО, GitHub, даты сдачи и дедлайна. Сортировка по дд и названию курса"""


async def get_teacher_deadline_notification_payload(
    teacher_telegram_id: int,
    assignment_id: int,
    session: AsyncSession
) -> Optional[Mapping[str, Any]]:
    """Данные для уведомления: сколько не сдали, список студентов, дедлайн."""


async def add_course_assistant(
    teacher_telegram_id: int,
    course_id: int,
    assistant_telegram_username: str,
    session: AsyncSession
) -> None:
    """Добавить ассистента по username. Только для учителя"""
    

async def remove_course_assistant(
    teacher_telegram_id: int,
    course_id: int,
    assistant_telegram_username: str,
    session: AsyncSession
) -> None:
    """Удалить ассистента. Только для учителя"""
    

async def create_course_announcement(
    teacher_telegram_id: int,
    course_id: int,
    text: str,
    session: AsyncSession
) -> None:
    """Создать объявление для курса. Только для учителя"""


async def trigger_manual_sync_for_teacher(
    course_id: int
    teacher_telegram_id: int,
    session: AsyncSession,
    github: GitHubClassroomClient
) -> bool:
    """Выполнить ручную синхронизацию данных по курсу. Только для учителя"""

```

### admin_commands.py

```python

async def grant_teacher_role(admin_telegram_id: int, target_telegram_username: str,
session: AsyncSession) -> None:
    """Выдать роль teacher."""
    

async def revoke_teacher_role(admin_telegram_id: int, target_telegram_username: str,
session: AsyncSession) -> None:
    """Отобрать роль teacher."""
    

async def ban_user(admin_telegram_id: int, target_telegram_username: str,
session: AsyncSession) -> None:
    """Забанить пользователя."""
    

async def unban_user(admin_telegram_id: int, target_telegram_username: str,
session: AsyncSession) -> None:
    """Разбанить пользователя."""
    

async def get_error_count_for_day(admin_telegram_id: int, day: Optional[date] = None,
session: AsyncSession) -> int:
    """Количество ошибок бота за указанный день, либо вся сводка ошибок. Сортировка по дате по убыванию."""

async def get_last_successful_github_call_time(admin_telegram_id: int,
session: AsyncSession) -> Optional[datetime]:
    """Последнее успешное обращение к GitHub."""
    

async def get_last_failed_github_call_info(admin_telegram_id: int,
session: AsyncSession) -> Optional[Mapping[str, Any]]:
    """Информация о последнем ошибочном обращении к GitHub."""

    
async def add_organisation(admin_telegram_id: int, teacher_telegram_id: int, name: str,
                           session: AsyncSession = None) -> None:
    """Добавляет организацию, в которой состоит учитель"""

```

### sync.py

   * Здесь лежат важные команды, которая обеспечивают синхронизацию нашей БД с гитхабом

   ```python
async def sync_function(session: AsyncSession) -> None:
    """Функция для перезаполнения БД
    :param session: AsyncSession
    :returns None"""

    
async def get_students_nearing_deadline(session: AsyncSession) -> set[tuple[int, str, str, str]]:
    """
    Вытащить (telegram_id, course_name, assignment_title, notification_time)
    для студентов, у которых желаемое время уведомления
    попадает в окно [NOW(), NOW() + 20 мин]
    Используется в scheduler
    :param session: AsyncSession
    :return tuple(tg_id, course_name, assignment_name)
    """

    
async def delete_overdued_states(session: AsyncSession) -> None:
    """Функция удаляет все просроченные OAuthStates
    :param session: AsyncSession
    :return None
    """

    
async def zero_sync_counter(session: AsyncSession) -> None:
    """Функция обнуляет все счетчики количества синхронизаций в полночь"""

   ```

## adapters

### table_to_text.py

   * Адаптер, который переводит результат запроса к БД в табличку вида

   ```
   Задание       | Дедлайн     | Статус    
   --------------+-------------+-----------
   HW1: Введение | 21.11 23:59 | в процессе
   HW2: Git      | 24.11 23:59 | не начато 
   HW3: ООП      | 28.11 23:59 | сдано
   ```

   Вместо ФИО выводятся фамилия и первая буква имени.
   Предлагаю реализовывать при помощи модуля prettytable. В процессе работы настроить максимальную ширину строки, возможно, незначительно изменить стиль таблицы

## infra


### config.py

   * Загружает данные из .env в константы

### db.py

   * Тут создается SessionFactory (асинхронная), engine для работы с БД. Важный момент: само описание БД лежит в models

### init_db.py

   * Это файл для инициализации БД, которая происходит только во время старта бота. Поскольку при инициализации старые таблицы не дропаются, а создаются только те, которых нет, такой способ для пет-проекта вполне жизнеспособный. 

### git/github_service.py
   
   * Осуществляет привязку аккаунта телеграм к гитхабу.

### git/router.py

   * Здесь лежит роутер, осуществляющий взаимодействие с API гитхаба.

### scheduler.py

   * Тут сидит шедулер, который с некоторой периодичностью 30 минут ходит в нашу бд и отправляет уведомления о дд. А также раз в 8 часов ходит в гитхаб и обновляет данные нашей бд.

### main.py

   * Точка входа. Вызывает инициализатор бд, запуск бота

### telegramm/app.py
 
   * Создает бота, диспетчер и хендлеры. Запускает работу бота

### telegram/keyboards

   * Тут лежат файлы .py со всеми клавиатурами (студента, препода, ассиста и админа)

### telegram/routers

   * Тут лежат файлы .py со всеми роутерами (общее взаимодействие, студента, препода, ассиста и админа). Внутри каждого роутера уже лежат хэндлеры (функции) соответствующих ролей. Именно здесь происходит обработка инпутов, вызов сценариев, отрисовка кнопок
# Картинка зависимостей

![](Зависимости.png)

# Кто что делает?

Web: научиться авторизоваться в гитхабе, ходить к гиту за данными. Делает Молонов Борис. Срок 3 недели (поскольку необходима плотная работа с блоком БД)

Бд: описать все бд, прописать инициализацию, запустить шедулер (это вместе с гитом делается) + научиться размещать весь проект вместе с бд в докере. 3 недели (поскольку для последнего этапа необходимо выполнение остальной части проекта) делает Бикмухаметов Тагир

Сценарии: заполнить весь  
Commands (кроме команд, которые требуют ходить в гитхаб. Их две). Делает Арзамасов Александр. Срок 2.5 недели

Бот: прописать инициализацию бота, обработку входа, вывод ответа, отрисовка клавиш. Делает Назаров Александр. Срок 2 недели.

Тесты: тесты на свои команды пишет каждый, кто писал их + проводится совместное ревью и дополнение тестов через 2 недели после начала работ (чтобы каждый участник смог посмотреть на чужой код, увидеть ошибки и придумать тесты, которые, сам кодер не приудмал). Делается в течение всей работы над проектом

# Репозиторий

https://github.com/BikTaIl/TG_Classroom_bot
