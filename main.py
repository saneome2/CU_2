#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Dependency Graph Visualization Tool')

    parser.add_argument('--package-name', required=True, help='Имя анализируемого пакета')
    parser.add_argument('--repo-url', required=True, help='URL-адрес репозитория или путь к файлу тестового репозитория')
    parser.add_argument('--test-mode', action='store_true', help='Режим работы с тестовым репозиторием')
    parser.add_argument('--version', help='Версия пакета')
    parser.add_argument('--output-file', default='graph.png', help='Имя сгенерированного файла с изображением графа')
    parser.add_argument('--ascii-tree', action='store_true', help='Режим вывода зависимостей в формате ASCII-дерева')

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # Обработка ошибок argparse
        print("Ошибка: Неправильные аргументы командной строки.")
        sys.exit(1)

    # Проверка на ошибки
    if not args.package_name:
        print("Ошибка: Имя пакета обязательно.")
        sys.exit(1)

    if not args.repo_url:
        print("Ошибка: URL репозитория или путь обязателен.")
        sys.exit(1)

    # Вывод параметров
    print("Параметры конфигурации:")
    print(f"package_name: {args.package_name}")
    print(f"repo_url: {args.repo_url}")
    print(f"test_mode: {args.test_mode}")
    print(f"version: {args.version}")
    print(f"output_file: {args.output_file}")
    print(f"ascii_tree: {args.ascii_tree}")

if __name__ == '__main__':
    main()