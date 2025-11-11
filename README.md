# Dependency Graph Visualization Tool

Инструмент для визуализации графа зависимостей пакетов Alpine Linux.

## Установка и запуск

1. Клонируйте репозиторий.
2. Запустите `python main.py` с параметрами.

## Параметры

- `--package-name`: Имя пакета (обязательно).
- `--repo-url`: URL репозитория или путь к тестовому файлу (обязательно).
- `--test-mode`: Режим тестового репозитория (флаг).
- `--version`: Версия пакета (обязательно).
- `--output-file`: Имя файла для сохранения (по умолчанию graph.png).
- `--ascii-tree`: Вывод в формате ASCII-дерева (флаг).

## Примеры

### Тестовый режим
```
python main.py --package-name A --repo-url test_graph.txt --test-mode --version dummy --ascii-tree
```

### Реальный режим
```
python main.py --package-name busybox --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/ --version 1.36.1-r7
```

## Вывод
- ASCII-дерево: на экран.
- D2: в файл .d2.
- SVG: в файл .svg.

## Этапы разработки
- Этап 1: Конфигурация (stage1_results.md).
- Этап 2: Сбор данных (stage2_results.md).
- Этап 3: Основные операции (stage3_results.md).
- Этап 4: Дополнительные операции (stage4_results.md).
- Этап 5: Визуализация (stage5_results.md).