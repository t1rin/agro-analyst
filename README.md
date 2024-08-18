# АгроАналитик

## Описание

Программа для сканирования местности и её анализа

## Возможности

- нейроанализ снимка

- показ снимков в удобном виджете

- сетка с сохранненными результатами анализа

- показ данных о снимке

## Запуск

Подключение виртуального окружения:

```shell
python3 -m venv venv
```

Выбираем в IDE созданное виртуальное окружение. Или по команде:

### Linux

```shell
source ./venv/bin/activate
```

или

### Windows

```shell
venv\Scripts\activate
```

### Далее

Загружаем библиотеки:

```shell
pip3 install -r requirements.txt
```

Запуск программы:

```shell
python3 main.py
```

## Структура

- `analyzer` - модуль для обработки снимков

- `data` - папка (динамичная) с новыми снимками (`images`) и уже обработанные (`results`)

- `config.py` - конфигурационный файл

- `templates.py` - файл текстовых шаблонов

## О работе программы

При запуске программы есть 3 вкладки:

- **главная**, на ней идет показ последнего полученного снимка

- **окно выбора** обработанных снимков

- **окно просмотра** выбранного снимка

Программа работает совместно с другой программой, которая присылает снимки в назначенную для этого папку. `agro-analyst` получает эти снимки и анализирует, результат анализа перемещает в другую папку, создав файл `.json` с его описанием

## Связь с программой "_съёмщиком_"

Программа "_съёмщик_" должна сохранять снимки в папку `data/images`. Если снимок **необходимо проанализировать**, нужно добавить описание снимка в файл `images.json`

Для снимка `data/images/image.jpg` файл `data/images/images.json` выглядит следующим образом:

```json
{
    "image.jpg": {
        "time": 1579522820,
        "coords": "20, 20"
    }
}
```

**Ключи для каждого отдельного снимка в файле `images.json`:**

- `time` - время в секундах с начала отчета

- `coords` - координаты снимка

Если анализ снимка **не нужен**, только вывод этого снимка в программу, имя снимка должно начинаться с `_`, а свойства можно задавать прямо в названии, разделяя их символом `_` (свойства можно менять в файле `templates.py`). Для свойства `x` и его значения ***25*** имя снимка может быть следующим: `_x_25.jpg` или `_x_25_image123.jpg` (`image123` - свободное название), предпочтительнее использование второго варианта

**Свойства для обычного снимка (без анализа):**

- `x` - глобальная позиция "_съёмщика_" по X

- `y` - глобальная позиция "_съёмщика_" по Y

- `localx` - локальная позиция "_съёмщика_" по X

- `localy` - локальная позиция "_съёмщика_" по Y

- `localz` - локальная позиция "_съёмщика_" по Z

#### Не рекомендуется:

Добавлять снимок без `_` в начале, не прописав затем его `images.json`

#### Рекомендуется
Добавлять снимок без `_`, прописав затем этот снимок в `images.json`

## **Примечания**

Модуль `analyzer` имеет далеко не окончательный вид. Текущее решение - это заглушка


Программа не готова корректно обрабатывать несколько перезаписей файла `images.json` за небольшой промежуток времени
