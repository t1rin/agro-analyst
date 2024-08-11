# АгроАналитик

## Описание

Программа для сканирования местности и её анализа

## Запуск

Подключение виртуального окружения:

```shell
python3 -m venv venv
```

```shell
pip3 install -r requirements.txt
```

Запуск программы:

```shell
python3 main.py
```

## Структура

- `analyzer` - модуль для обработки снимков

- `data` - папка с новыми снимками (`images`) и уже обработанные (`results`)

- `config.py` - конфигурационный файл

- `templates.py` - файл текстовых шаблонов

## О работе программы

При запуске программы есть 3 вкладки:

- главная, на ней идет показ последнего полученного снимка

- окно выбора обработанных снимков

- окно просмотра выбранного снимка

Программа работает совместно с другой программой, которая присылает снимки в назначенную для этого папку. agro-analyst получает эти снимки и обрабатывает, обработаные перемещает в другую папку создав файл `.json` с описанием анализа

## Связь с программой "съёмщиком"

Программа "съёмщик" должна сохранять снимки в папку `data/images`, а описание снимка добавлять в файл `images.json`. Ключи для каждого отдельного снимка в файле `.json`:

- `time` - время в секундах с начала отчета

- `coords` - координаты снимка

...

## Примечания

Модуль `analyzer` имеет далеко не окончательный вид. Текущее решение - это заглушка
