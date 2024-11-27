import unittest
import json
from main import read_config, get_commits, get_commit_files, build_dependency_graph, get_commit_parents
import os

class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.config = {
            "graphviz_path": "/usr/bin/dot",
            "repo_path": ".",
            "output_png_path": "graph.png",
            "tag_name": "HEAD"
        }

    def test_read_config(self):
        # Создаем временный конфигурационный файл
        config_path = 'temp_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f)
        config = read_config(config_path)
        self.assertEqual(config, self.config)
        os.remove(config_path)

    def test_get_commits(self):
        commits = get_commits(self.config['repo_path'], self.config['tag_name'])
        self.assertTrue(len(commits) > 0)

    def test_get_commit_files(self):
        commits = get_commits(self.config['repo_path'], self.config['tag_name'])
        files = get_commit_files(self.config['repo_path'], commits[0])
        self.assertIsInstance(files, list)

    def test_get_commit_parents(self):
        commits = get_commits(self.config['repo_path'], self.config['tag_name'])
        parents = get_commit_parents(self.config['repo_path'], commits[0])
        self.assertIsInstance(parents, list)

    def test_build_dependency_graph(self):
        commits = get_commits(self.config['repo_path'], self.config['tag_name'])
        graph = build_dependency_graph(commits, self.config['repo_path'])
        self.assertIsInstance(graph, dict)
        self.assertTrue(len(graph) > 0)



if __name__ == '__main__':
    unittest.main()
