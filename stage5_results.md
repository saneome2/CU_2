# Результаты выполнения этапа 5: Визуализация

## Описание
Реализована визуализация графа зависимостей: генерация текстового представления на языке D2, сохранение SVG-изображения и вывод ASCII-дерева (если --ascii-tree).

## Реализованная функциональность
- Генерация D2: текстовое описание графа с edges.
- Генерация SVG: простой hierarchical layout с rectangles и lines.
- ASCII-дерево: как в предыдущих этапах.

## Демонстрация для трех пакетов

### Пакет A (тестовый, без циклов)
Команда:
```
python main.py --package-name A --repo-url test_graph.txt --test-mode --version dummy
```

D2 (graph.d2):
```
A -> B
A -> C
B -> D
C -> D
E -> A
F -> G
G -> F
```

SVG сохранён в graph.svg (простой hierarchical layout).

ASCII-дерево (--ascii-tree):
```
└── A
    ├── B
    │   └── D
    └── C
        └── D
```

### Пакет F (тестовый, с циклом)
Команда:
```
python main.py --package-name F --repo-url test_graph.txt --test-mode --version dummy --output-file f_graph.png
```

D2 (f_graph.d2):
```
A -> B
A -> C
B -> D
C -> D
E -> A
F -> G
G -> F
```

SVG сохранён в f_graph.svg.

ASCII-дерево:
```
└── F
    └── G
        └── F (cycle)
```

### Пакет busybox (реальный, Alpine)
Команда:
```
python main.py --package-name busybox --repo-url https://dl-cdn.alpinelinux.org/alpine/v3.18/main/ --version 1.36.1-r7 --output-file busybox_graph.png
```

D2 (busybox_graph.d2):
```
busybox -> so:libc.musl-x86_64.so.1
```

SVG сохранён в busybox_graph.svg.

ASCII-дерево:
```
└── busybox
    └── so:libc.musl-x86_64.so.1
```

## Сравнение с штатными инструментами Alpine
Alpine не имеет встроенных инструментов визуализации зависимостей, но можно использовать `apk info -R <package>` для списка зависимостей или graphviz с dot для визуализации.

Пример: для busybox наш вывод — `so:libc.musl-x86_64.so.1`.

**Расхождения:**
- Наш инструмент показывает все из `D:` APKINDEX (включая libraries), а `apk info` показывает только пакеты (musl предоставляет libc).
- Визуализация: наш SVG — простой layout, штатные (graphviz) — более сложные алгоритмы позиционирования.
- Транзитивность: мы строим полный граф, штатные могут ограничиваться прямыми.