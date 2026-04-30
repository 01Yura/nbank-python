# Как работает фикстура `api_manager` — объяснение для новичков

Подробный разбор по шагам на примере теста `test_admin_can_create_user_with_valid_credentials` из файла
`src/tests/api/senior/create_user_api_test.py`.

---

## Оглавление

- [Что такое фикстура](#что-такое-фикстура)
- [Где определены фикстуры в проекте](#где-определены-фикстуры-в-проекте)
- [Что происходит при запуске теста — по шагам](#что-происходит-при-запуске-теста--по-шагам)
    - [Шаг 1. pytest видит, что тесту нужен `api_manager`](#шаг-1-pytest-видит-что-тесту-нужен-api_manager)
    - [Шаг 2. pytest идёт искать фикстуру `api_manager`](#шаг-2-pytest-идёт-искать-фикстуру-api_manager)
    - [Шаг 3. pytest сначала запускает `created_objects`](#шаг-3-pytest-сначала-запускает-created_objects)
    - [Шаг 4. pytest запускает
      `api_manager`, передавая туда список](#шаг-4-pytest-запускает-api_manager-передавая-туда-список)
    - [Шаг 5. Готовый `ApiManager` попадает в тест](#шаг-5-готовый-apimanager-попадает-в-тест)
    - [Шаг 6. Тест собирает DTO с входными данными](#шаг-6-тест-собирает-dto-с-входными-данными)
    - [Шаг 7. Тест зовёт
      `api_manager.admin_steps.create_user(...)`](#шаг-7-тест-зовёт-api_manageradmin_stepscreate_user)
    - [Шаг 8. Тело теста закончилось](#шаг-8-тело-теста-закончилось)
    - [Шаг 9. Запускается тейкдаун (то, что после `yield`)](#шаг-9-запускается-тейкдаун-то-что-после-yield)
    - [Шаг 10. Параметризация — всё повторяется заново](#шаг-10-параметризация--всё-повторяется-заново)
- [Ещё одна фикстура «за кулисами» — `auto_http_logger`](#ещё-одна-фикстура-за-кулисами--auto_http_logger)
- [Краткая схема жизненного цикла](#краткая-схема-жизненного-цикла)
- [Главные идеи, которые стоит запомнить](#главные-идеи-которые-стоит-запомнить)

---

## Что такое фикстура

Фикстура в `pytest` — это **функция-помощник**, которая **подготавливает что-то для теста заранее** (например, создаёт
объекты, подключения, данные), а после теста может **прибраться за собой** (удалить созданное, закрыть соединения и
т.д.).

> **Аналогия.** Представь, что тест — это повар, который готовит блюдо. Фикстура — это помощник на кухне, который **до
прихода повара** помыл овощи, поставил кастрюлю с водой на плиту, разложил приборы. А **после того как повар ушёл**,
> помощник помыл посуду и убрал со стола. Повар (тест) приходит на готовое и просто готовит. Ему не нужно думать о
> подготовке и уборке.

В `pytest` ты «заказываешь» фикстуру **просто указав её имя в аргументах теста** — pytest сам найдёт её и вызовет.

---

## Где определены фикстуры в проекте

В файле `conftest.py` (это особое имя — pytest автоматически подхватывает фикстуры оттуда):

```python
@pytest.fixture
def created_objects():
    objects: list[Any] = []
    yield objects

    cleanup_objects(objects)


@pytest.fixture
def api_manager(created_objects):
    return ApiManager(created_objects)
```

Здесь две фикстуры: `created_objects` и `api_manager`. Причём `api_manager` **зависит от** `created_objects` (она
указана у неё в аргументах). Это очень важно — мы это разберём ниже.

---

## Что происходит при запуске теста — по шагам

Возьмём один прогон твоего параметризованного теста, например с параметрами `("Qz8", "Aa1!aaaa", "USER")`:

```python
def test_admin_can_create_user_with_valid_credentials(self, api_manager: ApiManager, username, password, role):
    # create a user
    create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
    api_manager.admin_steps.create_user(create_user_request_dto)
```

### Шаг 1. pytest видит, что тесту нужен `api_manager`

В сигнатуре теста есть аргумент `api_manager: ApiManager`. Дополнительно сверху стоит декоратор:

```python
@pytest.mark.usefixtures("api_manager")
```

Любой из этих двух способов говорит pytest: «перед запуском этого теста подготовь фикстуру `api_manager`».

> **Нюанс.** `@pytest.mark.usefixtures("api_manager")` тут немного избыточен, потому что `api_manager` уже есть в
> аргументах теста. Достаточно было бы чего-то одного. Но это не ошибка — работает.

### Шаг 2. pytest идёт искать фикстуру `api_manager`

Находит её в `conftest.py`:

```python
@pytest.fixture
def api_manager(created_objects):
    return ApiManager(created_objects)
```

И видит: «ага, чтобы создать `api_manager`, мне сначала нужна другая фикстура — `created_objects`». Это **цепочка
зависимостей**. pytest сам разрулит порядок.

### Шаг 3. pytest сначала запускает `created_objects`

```python
@pytest.fixture
def created_objects():
    objects: list[Any] = []
    yield objects

    cleanup_objects(objects)
```

Что тут происходит:

1. Создаётся **пустой список** `objects = []`.
2. Команда `yield objects` — это «отдать список тесту и поставить выполнение фикстуры на паузу». Всё, что после `yield`,
   выполнится **позже, после теста**.

Этот пустой список — это будущий «список созданных в тесте объектов, которые потом надо будет удалить».

### Шаг 4. pytest запускает `api_manager`, передавая туда список

```python
@pytest.fixture
def api_manager(created_objects):
    return ApiManager(created_objects)
```

`created_objects` здесь — это **тот самый пустой список**, который нам только что дала предыдущая фикстура. Pytest
подставил его автоматически.

Дальше создаётся объект `ApiManager(created_objects)`:

```python
class ApiManager:
    def __init__(self, created_objects: list):
        self.admin_steps = AdminSteps(created_objects)
```

Конструктор `ApiManager` принимает список и **прокидывает его дальше** в `AdminSteps`.

А `AdminSteps` наследуется от `BaseSteps`, и в нём список сохраняется в поле `self.created_objects`:

```python
class BaseSteps:
    def __init__(self, created_objects: list[Any]):
        self.created_objects = created_objects
```

> **Ключевая идея.** Список один и тот же на всех уровнях. Это **тот же объект в памяти** — `conftest.py` держит на него
> ссылку и `AdminSteps` тоже. Если кто-то добавит в него элемент, оба «увидят» это изменение.

### Шаг 5. Готовый `ApiManager` попадает в тест

`return ApiManager(...)` возвращает объект, и pytest **подставляет** его в аргумент теста `api_manager: ApiManager`.
Теперь тест начинает выполняться.

### Шаг 6. Тест собирает DTO с входными данными

```python
create_user_request_dto = CreateUserRequestDTO(username=username, password=password, role=role)
```

Здесь `username`, `password`, `role` — это значения из текущего параметризованного набора (например,
`"Qz8", "Aa1!aaaa", "USER"`). Они подставляются благодаря `@pytest.mark.parametrize`.

### Шаг 7. Тест зовёт `api_manager.admin_steps.create_user(...)`

```python
api_manager.admin_steps.create_user(create_user_request_dto)
```

Что происходит внутри:

```python
def create_user(self, create_user_request_dto: CreateUserRequestDTO):
    # create a user
    create_user_response = AdminClient(
        RequestSpec.auth_as_admin_spec(),
        ResponseSpec.response_returns_201_spec()).post(
        create_user_request_dto)

    create_user_response_dto = CreateUserResponseDTO(**create_user_response.json())
    # ассерты
    assert create_user_response_dto.username == create_user_request_dto.username
    assert create_user_response_dto.role == create_user_request_dto.role
    password_hash = create_user_response_dto.password
    assert isinstance(password_hash, str) and len(password_hash.strip()) > 0

    self.created_objects.append(create_user_response_dto)

    return create_user_response_dto
```

По шагам:

1. `AdminClient(...).post(...)` — отправляет HTTP-запрос на создание пользователя и проверяет, что пришёл статус **201
   **.
2. Из JSON-ответа собирается `CreateUserResponseDTO`.
3. Делаются `assert`-ы: что в ответе тот же `username`, та же `role`, и что пароль вернулся как непустая строка-хэш. *
   *Это и есть «ассерты, зашитые в метод»**, про которые написано в комментарии к тесту.
4. **Самая важная для нашей фикстуры строка:**

   ```python
   self.created_objects.append(create_user_response_dto)
   ```

   Созданный пользователь кладётся в **тот самый список**, который пришёл из фикстуры `created_objects`. Таким образом
   фикстура «узнаёт», что в этом тесте появился новый пользователь, которого потом надо удалить.

### Шаг 8. Тело теста закончилось

После последней строки у теста больше нет инструкций. pytest считает, что тест завершён (если не было упавших ассертов —
он зелёный).

### Шаг 9. Запускается тейкдаун (то, что после `yield`)

Помнишь, мы остановились на `yield objects`? Теперь pytest продолжает фикстуру дальше:

```python
    cleanup_objects(objects)
```

А вот и сам клинап:

```python
def cleanup_objects(objects: list[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserResponseDTO):
            api_manager.admin_steps.delete_user(obj.id)
        else:
            logging.warning(f"Object type: {type(obj)} is not deleted")
```

Что тут происходит:

1. Создаётся **новый** `ApiManager` (нужен только чтобы достать `admin_steps` и использовать `delete_user`).
2. Идём по списку `objects` (в нём сейчас лежит созданный в тесте пользователь).
3. Для каждого `CreateUserResponseDTO` вызывается `delete_user(obj.id)` — то есть HTTP `DELETE` по id.

Так база остаётся чистой: каждый тест убирает за собой сам.

### Шаг 10. Параметризация — всё повторяется заново

У теста 4 набора параметров в `parametrize`. **Для каждого набора весь цикл выше повторяется отдельно с нуля:**

- новый пустой `created_objects`,
- новый `ApiManager`,
- запуск теста,
- клинап.

Это потому что у фикстур по умолчанию `scope="function"` — то есть «новая фикстура на каждый прогон тест-функции». Если
бы там стоял `scope="module"` или `scope="session"`, фикстура переиспользовалась бы, но тут это не наш случай.

---

## Ещё одна фикстура «за кулисами» — `auto_http_logger`

В `conftest.py` есть ещё одна фикстура:

```python
@pytest.fixture(autouse=True)
def auto_http_logger(request, monkeypatch):
    # проверяем, есть ли marker у теста
    if request.node.get_closest_marker("log_http") is None:
        return

    original_request = requests.sessions.Session.request

    def patched_request(self, method, url, **kwargs):
        response = original_request(self, method, url, **kwargs)
        log_response(response)
        return response

    monkeypatch.setattr(requests.sessions.Session, "request", patched_request)
```

`autouse=True` означает: «применяй меня к **каждому** тесту автоматически, даже если меня никто не просил». Внутри она
проверяет, есть ли у теста маркер `@pytest.mark.log_http`. Если нет — выходит, ничего не делая. Если есть — подменяет
`requests.Session.request` так, чтобы каждый HTTP-запрос/ответ логировался цветным выводом.

---

## Краткая схема жизненного цикла

Один прогон одного параметризованного теста:

1. pytest видит параметризацию → берёт первый набор (`"Qz8", "Aa1!aaaa", "USER"`).
2. pytest видит, что тесту нужен `api_manager` → идёт его готовить.
3. `api_manager` зависит от `created_objects` → pytest сначала запускает `created_objects`.
4. `created_objects` создаёт пустой `[]`, делает `yield` — отдаёт его наверх.
5. `api_manager` получает этот `[]`, делает `ApiManager([])`, который пробрасывает список в `AdminSteps`. Возвращает
   `ApiManager`.
6. pytest запускает тест и передаёт в него готовый `ApiManager`.
7. Тест зовёт `admin_steps.create_user(...)` → пользователь создаётся через API, проверяется ответ, **созданный DTO
   кладётся в тот же `[]`**.
8. Тест завершён.
9. pytest возвращается в `created_objects` после `yield` → вызывает `cleanup_objects(objects)` → удаляет всех
   пользователей из списка.
10. pytest переходит к следующему набору параметров и повторяет шаги 2–9 с нуля.

### Визуально

```
[parametrize: набор N]
        │
        ▼
┌─────────────────────────────────┐
│ created_objects: objects = []   │  ← setup
│         yield objects           │
└──────────────┬──────────────────┘
               │ (тот же список)
               ▼
┌─────────────────────────────────┐
│ api_manager:                    │  ← setup
│   ApiManager(objects)           │
│     └─ AdminSteps(objects)      │
│           └─ self.created_      │
│              objects = objects  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ ТЕСТ                            │
│  create_user(...)               │
│    → POST /users                │
│    → assert ...                 │
│    → objects.append(user_dto)   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ cleanup_objects(objects):       │  ← teardown
│   for obj in objects:           │
│       admin_steps.delete_user() │
└─────────────────────────────────┘
```

---

## Главные идеи, которые стоит запомнить

- **Фикстура** = функция, помеченная `@pytest.fixture`, которая готовит данные/окружение для теста.
- Чтобы тест «получил» фикстуру, достаточно **указать её имя в аргументах теста** (или использовать
  `@pytest.mark.usefixtures`).
- Фикстуры могут **зависеть друг от друга** (просто указывают друг друга в аргументах). pytest сам выстраивает порядок
  вызова.
- `yield` внутри фикстуры разделяет её на две части: **до теста (setup)** и **после теста (teardown)**.
- В этом проекте главный трюк — **общий список `created_objects`** между фикстурой и `AdminSteps`. Тест пополняет
  список, фикстура потом по нему чистит.
- `conftest.py` — особенный файл: pytest сам подхватывает оттуда фикстуры, **импортировать их вручную не нужно** (импорт
  `from conftest import api_manager` в тестовом файле на самом деле лишний — фикстуру pytest нашёл бы и без него).
