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
        graph, error = load_test_graph(repo_url)
        if error:
            return [], True
        return graph.get(package_name, []), False
    else:
        apkindex_url = f"{repo_url}x86_64/APKINDEX.tar.gz"
        try:
            with urllib.request.urlopen(apkindex_url) as response:
                apkindex_data = response.read()
        except Exception as e:
            print(f"Ошибка при скачивании APKINDEX: {e}")
            return [], True

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
                                    return current_package.get('depends', []), False
        except Exception as e:
            print(f"Ошибка при обработке APKINDEX: {e}")
            return [], True
    return [], False

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
        return graph, False
    except Exception as e:
        print(f"Ошибка при чтении тестового графа: {e}")
        return defaultdict(list), True

def build_dependency_graph(package, version, repo_url, test_mode):
    all_deps = set()
    visited = set()
    stack = [package]
    error_occurred = False
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        if current == package:
            deps, error = get_direct_dependencies(current, repo_url, test_mode, version)
        else:
            deps, error = get_direct_dependencies(current, repo_url, test_mode)
        if error:
            error_occurred = True
            break
        for dep in deps:
            if dep not in visited:
                stack.append(dep)
            all_deps.add(dep)
    return all_deps, error_occurred

def generate_d2(graph):
    lines = []
    for node in graph:
        for dep in graph[node]:
            lines.append(f"{node} -> {dep}")
    return "\n".join(lines)

def generate_svg_tree(graph, root):
    positions = {}
    def assign_positions(node, x, y):
        if node in positions:
            return
        positions[node] = (x, y)
        deps = graph.get(node, [])
        width = max(100, len(deps) * 120)
        start_x = x - width // 2 + 60
        for i, dep in enumerate(deps):
            assign_positions(dep, start_x + i * 120, y + 100)
    
    assign_positions(root, 400, 50)
    
    svg = '<?xml version="1.0" encoding="UTF-8"?>\n<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">\n'
    # Draw edges
    for node in graph:
        if node in positions:
            x1, y1 = positions[node]
            for dep in graph[node]:
                if dep in positions:
                    x2, y2 = positions[dep]
                    svg += f'  <line x1="{x1+50}" y1="{y1+50}" x2="{x2+50}" y2="{y2}" stroke="black" stroke-width="2" />\n'
    # Draw nodes
    for node, (x, y) in positions.items():
        svg += f'  <rect x="{x}" y="{y}" width="100" height="50" fill="lightblue" stroke="black" stroke-width="2" rx="5" />\n'
        svg += f'  <text x="{x+50}" y="{y+30}" text-anchor="middle" font-family="Arial" font-size="12">{node}</text>\n'
    svg += '</svg>\n'
    return svg

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
    all_deps, error = build_dependency_graph(args.package_name, args.version, args.repo_url, args.test_mode)
    if error:
        sys.exit(1)

    if args.ascii_tree:
        # Build graph for tree
        graph = defaultdict(list)
        if args.test_mode:
            graph, _ = load_test_graph(args.repo_url)
        else:
            # For real mode, build partial graph
            visited = set()
            stack = [args.package_name]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                deps, _ = get_direct_dependencies(current, args.repo_url, args.test_mode, args.version if current == args.package_name else None)
                graph[current] = deps
                for dep in deps:
                    if dep not in visited:
                        stack.append(dep)
        print_ascii_tree(args.package_name, graph)
    else:
        # Build graph
        graph = defaultdict(list)
        if args.test_mode:
            graph, _ = load_test_graph(args.repo_url)
        else:
            # For real mode, build partial graph
            visited = set()
            stack = [args.package_name]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                deps, _ = get_direct_dependencies(current, args.repo_url, args.test_mode, args.version if current == args.package_name else None)
                graph[current] = deps
                for dep in deps:
                    if dep not in visited:
                        stack.append(dep)
        # Generate D2
        d2_content = generate_d2(graph)
        d2_file = args.output_file.replace('.png', '.d2')
        with open(d2_file, 'w') as f:
            f.write(d2_content)
        print(f"D2 представление сохранено в {d2_file}")
        # Generate SVG
        svg_content = generate_svg_tree(graph, args.package_name)
        svg_file = args.output_file.replace('.png', '.svg')
        with open(svg_file, 'w') as f:
            f.write(svg_content)
        print(f"SVG изображение сохранено в {svg_file}")

if __name__ == '__main__':
    main()