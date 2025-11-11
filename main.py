#!/usr/bin/env python3
import argparse
import sys
import urllib.request
import tarfile
import io
from collections import defaultdict

def get_direct_dependencies(package_name, repo_url, test_mode, version=None):
    if test_mode:
        # For test mode, repo_url is path to file describing graph
        graph = load_test_graph(repo_url)
        return graph.get(package_name, [])
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
                            if current_package.get('name') == package_name:
                                if version is None or current_package.get('version') == version:
                                    return current_package.get('depends', [])
        except Exception as e:
            print(f"Ошибка при обработке APKINDEX: {e}")
            return []
    return []

def load_test_graph(file_path):
    graph = defaultdict(list)
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    package, deps = line.split(':', 1)
                    package = package.strip()
                    deps = deps.strip().split()
                    graph[package] = deps
    except Exception as e:
        print(f"Ошибка при чтении тестового графа: {e}")
    return graph

def build_dependency_graph(package, version, repo_url, test_mode):
    all_deps = set()
    visited = set()
    stack = [package]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        if current == package:
            deps = get_direct_dependencies(current, repo_url, test_mode, version)
        else:
            deps = get_direct_dependencies(current, repo_url, test_mode)
        for dep in deps:
            if dep not in visited:
                stack.append(dep)
            all_deps.add(dep)
    return all_deps

def print_ascii_tree(package, graph, prefix="", is_last=True, visited=None):
    if visited is None:
        visited = set()
    if package in visited:
        print(prefix + ("└── " if is_last else "├── ") + package + " (cycle)")
        return
    visited.add(package)
    print(prefix + ("└── " if is_last else "├── ") + package)
    deps = graph.get(package, [])
    for i, dep in enumerate(deps):
        extension = "    " if is_last else "│   "
        print_ascii_tree(dep, graph, prefix + extension, i == len(deps) - 1, visited.copy())  # copy to allow revisits in other branches

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

    # Построение графа зависимостей
    all_deps = build_dependency_graph(args.package_name, args.version, args.repo_url, args.test_mode)

    if args.ascii_tree:
        # Build graph for tree
        graph = defaultdict(list)
        if args.test_mode:
            graph = load_test_graph(args.repo_url)
        else:
            # For real mode, build partial graph
            visited = set()
            stack = [args.package_name]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                deps = get_direct_dependencies(current, args.repo_url, args.test_mode, args.version if current == args.package_name else None)
                graph[current] = deps
                for dep in deps:
                    if dep not in visited:
                        stack.append(dep)
        print_ascii_tree(args.package_name, graph)
    else:
        # Save to file
        with open(args.output_file, 'w') as f:
            f.write(f"Dependency graph for {args.package_name}:\n")
            for dep in sorted(all_deps):
                f.write(f"{dep}\n")
        print(f"Граф зависимостей сохранён в {args.output_file}")

if __name__ == '__main__':
    main()