import requests
import os
import json
import time

class Config:
    local_path = '/home/jing/Dropbox/Learning/Leetcode'
    github_leetcode_url = 'https://github.com/jshota/leetcode-solutions'
    leetcode_url = 'https://leetcode.com/problems/'

class Problem:
    """
    Store the content of Leetcode problems.
    """

    def __init__(self, id_, name, url, lock, difficulty):
        self.id_ = id_
        self.title = name
        self.url = url
        self.lock = lock
        self.difficulty = difficulty

        # solution url
        self.python = ''

class TableContent:
    """
    Request problems content and form them as a table.
    """

    def __init__(self):
        self.problems = []
        self.table = []
        self.table_item = {}
        self.lock = ''

    def get_leetcode_problems(self):
        """
        acquire problems content from Leetcode api
        """
        content = requests.get('https://leetcode.com/api/problems/algorithms/').content
        self.problems = json.loads(content)['stat_status_pairs']
        difficultys = ['Easy', 'Medium', 'Hard']
        for i in range(len(self.problems)-1, -1, -1):

            # grab the problem's attributes
            problem = self.problems[i]
            name = problem['stat']['question__title']
            url = problem['stat']['question__title_slug']
            id_ = str(problem['stat']['frontend_question_id'])
            lock = problem['paid_only']
            if lock:
                self.lock = 'Prime'
            else:
                self.lock = 'Free'
            difficulty = difficultys[problem['difficulty']['level'] - 1]
            url = Config.leetcode_url + url + '/description/'
            
            # create the problem instance and append it into a hash-table
            p = Problem(id_, name, url, self.lock, difficulty)
            self.table.append(p.id_)
            self.table_item[p.id_] = p
        return self.table_item

class Readme:
    """
    Generate Readme file for one problem.
    """

    def __init__(self, id_, table_instance):
        """
        :param id_: problem number
        :param table_instance: problems table instance
        """
        self.id_ = id_

        # initial problem's attributes
        item = table_instance[self.id_]
        self.title = item.title
        self.url = item.url
        self.lock = item.lock
        self.difficulty = item.difficulty
        
    def create_readme(self):
        """
        create the readme file
        :return:
        """
        file_path = Config.local_path + '/pending/' + self.id_ + '.' + self.title + '.md'
        with open(file_path, 'w') as f:
            f.write('# ' + self.id_ + '.' + self.title + '\n\n')
            f.write('## Tags\n\n')
            f.write('- ' + self.lock + '\n')
            f.write('- ' + self.difficulty + '\n')
            f.write('- Frequency: /5\n\n')

            f.write('## Links\n\n')
            f.write('[Leetcode]({})\n'.format(self.url))
            f.write('[Blog](http://206.81.6.248:12306/leetcode/{}/description)\n'.format(self.title.lower().replace(' ', '-')))
            f.write('## Description\n\n' + '> Description here...\n\n')
            f.write('## Python code\n\n')
            f.write('```python\n\n' + '```\n\n')
            f.write('## Animation\n\n' + 'None\n\n')
            f.write('## Reference\n\n' + 'None\n')

def main():
    id_ = input("Problem Number: ")
    table_instance = TableContent().get_leetcode_problems()
    Readme(id_, table_instance).create_readme()

if __name__ == '__main__':
    main()