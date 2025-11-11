# Результаты выполнения этапа 1: Минимальный прототип с конфигурацией

## Описание
Создано минимальное CLI-приложение на Python для визуализации графа зависимостей. Приложение использует библиотеку `argparse` для обработки командной строки.

## Реализованные параметры
- `--package-name`: Имя анализируемого пакета (обязательный)
- `--repo-url`: URL-адрес репозитория или путь к файлу тестового репозитория (обязательный)
- `--test-mode`: Режим работы с тестовым репозиторием (булевый флаг)
- `--version`: Версия пакета (опциональный)
- `--output-file`: Имя сгенерированного файла с изображением графа (по умолчанию 'graph.png')
- `--ascii-tree`: Режим вывода зависимостей в формате ASCII-дерева (булевый флаг)

## Обработка ошибок
- Если не указан `--package-name`, выводится ошибка "Ошибка: Имя пакета обязательно."
- Если не указан `--repo-url`, выводится ошибка "Ошибка: URL репозитория или путь обязателен."
- Неправильные аргументы командной строки обрабатываются `argparse` с выводом "Ошибка: Неправильные аргументы командной строки."

## Демонстрация запуска

### Пример успешного запуска:
```
python main.py --package-name requests --repo-url https://github.com/psf/requests --version 2.25.1 --output-file deps.png --ascii-tree
```

Вывод:
```
Параметры конфигурации:
package_name: requests
repo_url: https://github.com/psf/requests
test_mode: False
version: 2.25.1
output_file: deps.png
ascii_tree: True
```

### Пример с ошибкой (отсутствует обязательный параметр):
```
python main.py --repo-url https://github.com/psf/requests
```

Вывод:
```
usage: main.py [-h] --package-name PACKAGE_NAME --repo-url REPO_URL [--test-mode]
               [--version VERSION] [--output-file OUTPUT_FILE] [--ascii-tree]
main.py: error: the following arguments are required: --package-name
Ошибка: Неправильные аргументы командной строки.
```

### Пример с неправильными аргументами:
```
python main.py --invalid-arg
```

Вывод:
```
usage: main.py [-h] --package-name PACKAGE_NAME --repo-url REPO_URL [--test-mode]
               [--version VERSION] [--output-file OUTPUT_FILE] [--ascii-tree]
main.py: error: the following arguments are required: --package-name, --repo-url
Ошибка: Неправильные аргументы командной строки.
```