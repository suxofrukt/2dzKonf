import json
import subprocess
import os
import sys
from typing import List, Dict

def read_config(config_path: str) -> Dict:
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл не найден по пути: {config_path}")
        sys.exit(1)
    with open(config_path, 'r') as f:
        config = json.load(f)
    required_keys = ['graphviz_path', 'repo_path', 'output_png_path', 'tag_name']
    for key in required_keys:
        if key not in config:
            print(f"Отсутствует ключ '{key}' в конфигурационном файле.")
            sys.exit(1)
    return config

def get_commits(repo_path: str, tag_name: str) -> List[str]:
    cmd = ['git', '-C', repo_path, 'rev-list', tag_name]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Ошибка при получении коммитов: {result.stderr}")
        sys.exit(1)
    commits = result.stdout.strip().split('\n')
    return commits

def get_commit_files(repo_path: str, commit_hash: str) -> List[str]:
    cmd = ['git', '-C', repo_path, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Ошибка при получении файлов коммита {commit_hash}: {result.stderr}")
        sys.exit(1)
    files = result.stdout.strip().split('\n')
    return files

def build_dependency_graph(commits: List[str], repo_path: str) -> Dict[str, Dict]:
    graph = {}
    for commit in commits:
        files = get_commit_files(repo_path, commit)
        parents = get_commit_parents(repo_path, commit)
        graph[commit] = {
            'files': files,
            'parents': parents
        }
    return graph

def get_commit_parents(repo_path: str, commit_hash: str) -> List[str]:
    cmd = ['git', '-C', repo_path, 'rev-list', '--parents', '-n', '1', commit_hash]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Ошибка при получении родителей коммита {commit_hash}: {result.stderr}")
        sys.exit(1)
    parts = result.stdout.strip().split()
    return parts[1:]  # Первым элементом является сам коммит

def generate_graphviz_file(graph: Dict[str, Dict], output_dot_path: str):
    with open(output_dot_path, 'w') as f:
        f.write('digraph G {\n')
        for commit, data in graph.items():
            label = f"Commit: {commit[:7]}\\nFiles:\\n" + "\\n".join(data['files'])
            f.write(f'"{commit}" [label="{label}"];\n')
        for commit, data in graph.items():
            for parent in data['parents']:
                if parent in graph:
                    f.write(f'"{parent}" -> "{commit}";\n')
        f.write('}\n')

def visualize_graph(graphviz_path: str, input_dot_path: str, output_png_path: str):
    cmd = [graphviz_path, '-Tpng', input_dot_path, '-o', output_png_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Ошибка при визуализации графа: {result.stderr}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Использование: python main.py <путь_к_конфигурационному_файлу>")
        sys.exit(1)
    config_path = sys.argv[1]
    config = read_config(config_path)
    graphviz_path = config['graphviz_path']
    repo_path = config['repo_path']
    output_png_path = config['output_png_path']
    tag_name = config['tag_name']
    output_dot_path = 'graph.dot'

    commits = get_commits(repo_path, tag_name)
    graph = build_dependency_graph(commits, repo_path)
    generate_graphviz_file(graph, output_dot_path)
    visualize_graph(graphviz_path, output_dot_path, output_png_path)
    os.remove(output_dot_path)
    print("Граф зависимостей успешно построен и сохранен в файл:", output_png_path)

if __name__ == "__main__":
    main()
