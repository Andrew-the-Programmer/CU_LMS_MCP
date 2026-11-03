# CU LMS MCP

MCP-сервер для сервиса Центрального Университета - LMS. Даёт агенту доступ к твоим курсам, материалам и заданиям.

**Только чтение.** Сервер ничего не отправляет, не меняет и не удаляет в LMS.

## Что можно получить

- профиль студента;
- список курсов (по умолчанию первые 25);
- недели курса;
- материалы внутри недели: файлы, картинки, видео, аудио, текст;
- домашние задания: описание и файлы;
- тесты: вопросы и варианты ответов;
- ссылки на скачивание файлов.

Что обычно лежит внутри недели:

- **Материалы** — файлы, картинки, видео, аудио или текст.
- **ДЗ** — описание задания и файлы.
- **Тест** — вопросы и варианты ответов, без файлов.
- Может быть и другой блок — сервер вернёт то, что реально есть в LMS.

Курс → Неделя → Материалы / ДЗ / Тест

## Установка

Нужен Python 3.14+ и [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/Andrew-the-Programmer/CU_LMS_MCP.git
cd CU_LMS_MCP
poetry install
cp example.env .env
```

## Как взять `bff.cookie`

1. Зайди на <https://my.centraluniversity.ru>.
2. Открой DevTools: `F12` → вкладка **Application** (в Firefox — **Storage**).
3. Слева выбери **Cookies** → `https://my.centraluniversity.ru`.
4. Найди cookie с именем `bff.cookie` и скопируй **Value**.
5. Вставь значение в `.env`:

```dotenv
CU_LMS_SESSION_COOKIE=сюда_вставь_cookie
```

Cookie даёт доступ к аккаунту. Не коммить `.env` и не показывай cookie другим.

## Запуск

```bash
poetry run python -m cu_lms_mcp.server
```

Сервер работает через stdio, HTTP-порт не открывается.

## Подключение к Hermes

Конфиг Hermes: `~/.hermes/config.yaml`.

```yaml
mcp_servers:
  cu_lms:
    command: /абсолютный/путь/до/venv/bin/python
    args:
      - -m
      - cu_lms_mcp.server
    env:
      CU_LMS_SESSION_COOKIE: "сюда_вставь_cookie"
```

Путь до Python можно узнать так:

```bash
poetry env info --executable
```

## Инструменты

| Инструмент | Что делает |
| --- | --- |
| `get_student_profile` | Профиль студента |
| `list_student_courses` | Список курсов, можно задать `limit`, `offset`, `state` |
| `get_course_summary` | Информация о курсе |
| `get_course_overview` | Недели курса и что в них лежит |
| `get_course_theme_summary` | Информация о неделе |
| `get_longread_summary` | Информация о блоке внутри недели |
| `get_longread_materials` | Содержимое блока: материалы, ДЗ или тест |
| `get_task` | ДЗ или тест |
| `generate_content_download_link` | Ссылка на скачивание файла |

Если в неделе лежит ДЗ или тест, сервер умеет открыть его отдельно.

## Тесты

```bash
poetry run pytest
```

Тесты ходят в настоящий LMS и требуют рабочий cookie в `.env`.

Что проверяют:

- `test_get_student_profile` — что профиль студента загружается.
- `test_all_tools` — берёт один курс и проходит по нему: недели → материалы,
  ДЗ и тесты. Для файлов генерирует ссылки на скачивание, для ДЗ и тестов
  запрашивает задание. Проверяет, что ответы LMS соответствуют ожидаемому
  формату.

Если нужны логи во время выполнения:

```bash
poetry run pytest -v -s --log-cli-level=INFO
```

Если тесты падают с 401 — скорее всего, истёк cookie. Возьми новый и обнови `.env`.

## Документация

- OpenAPI-спека: [`api_docs.yaml`](api_docs.yaml)
- Для разработки: [`AGENT.md`](AGENT.md)
- Интерактивная документация API: [открыть](https://cu-devs-collective.github.io/open-cu-services-sdk/api-docs/?url=https://raw.githubusercontent.com/cu-devs-collective/open-cu-services-sdk/spec/lmsapi/v0.1.0/spec/lmsapi/lmsapi.re.openapi.yaml#/)
