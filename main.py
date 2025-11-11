#!/usr/bin/env python3
import argparse
import sys
import urllib.request
import tarfile
import io

def get_dependencies(package_name, version, repo_url, test_mode):
    if test_mode:
        apkindex_path = repo_url
        with open(apkindex_path, 'rb') as f:
            apkindex_data = f.read()
    else:
        apkindex_url = f"{repo_url}x86_64/APKINDEX.tar.gz"
        try:
            with urllib.request.urlopen(apkindex_url) as response:
                apkindex_data = response.read()
        except Exception as e:
            print(f"Ошибка при скачивании APKINDEX: {e}")
            return []

    try:
        with tarfile.open(fileobj=io.BytesIO(apkindex_data), mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name == 'APKINDEX':
                    f = tar.extractfile(member)
                    content = f.read().decode('utf-8', errors='ignore')
                    entries = content.split('C:')
                    for entry in entries[1:]:  # skip first empty
                        lines = ('C:' + entry).split('\n')
                        current_package = {}
                        for line in lines:
                            if line.startswith('P:'):
                                current_package['name'] = line[2:].strip()
                            elif line.startswith('V:'):
                                current_package['version'] = line[2:].strip()
                            elif line.startswith('D:'):
                                current_package['depends'] = line[2:].strip().split()
                        if current_package.get('name') == package_name and current_package.get('version') == version:
                            return current_package.get('depends', [])
    except Exception as e:
        print(f"Ошибка при обработке APKINDEX: {e}")
        return []
    return []

def main():
    parser = argparse.ArgumentParser(description='Dependency Graph Visualization Tool')

    parser.add_argument('--package-name', required=True, help='Имя анализируемого пакета')
    parser.add_argument('--repo-url', required=True, help='URL-адрес репозитория или путь к файлу тестового репозитория')
    parser.add_argument('--test-mode', action='store_true', help='Режим работы с тестовым репозиторием')
    parser.add_argument('--version', required=True, help='Версия пакета')
    parser.add_argument('--output-file', default='graph.png', help='Имя сгенерированного файла с изображением графа')
    parser.add_argument('--ascii-tree', action='store_true', help='Режим вывода зависимостей в формате ASCII-дерева')

    try:
        args = parser.parse_args()
    except SystemExit as e:
        print("Ошибка: Неправильные аргументы командной строки.")
        sys.exit(1)

    # Проверка на ошибки
    if not args.package_name:
        print("Ошибка: Имя пакета обязательно.")
        sys.exit(1)

    if not args.repo_url:
        print("Ошибка: URL репозитория или путь обязателен.")
        sys.exit(1)

    if not args.version:
        print("Ошибка: Версия пакета обязательна.")
        sys.exit(1)

    # Получение зависимостей
    dependencies = get_dependencies(args.package_name, args.version, args.repo_url, args.test_mode)
    if dependencies:
        print("Прямые зависимости:")
        for dep in dependencies:
            print(dep)
    else:
        print("Зависимости не найдены.")

if __name__ == '__main__':
    main()