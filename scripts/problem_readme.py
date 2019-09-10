import requests
import os
import json
import time
from scipy import io
from lxml import html
from bs4 import BeautifulSoup

class Config:
    local_path = '..'
    local_gifs_path = local_path + '/gifs/'
    local_pending_path = local_path + '/pending/'
    local_data_file_name = 'data.mat'
    holder_gif = 'pending gif...'
    
    github_leetcode_url = 'https://github.com/jshota/leetcode-solutions'
    github_gif_url = 'https://github.com/jshota/leetcode-solutions/blob/master/gifs/'
    
    leetcode_url = 'https://leetcode.com/problems/'
    
    blog_url = 'http://206.81.6.248:12306/leetcode/'
    blog_search_url = blog_url + 'search/'

class Data:
    """
    Store and load local data
    """
    def __init__(self):
        if os.path.isfile(Config.local_data_file_name):
            self.data = io.loadmat(Config.local_data_file_name)
        else:
            self.data = {}

    def write(self, key, value):
        """
        :type key: str
        :param value: the value needs to store
        """
        self.data[key] = value
        io.savemat(Config.local_data_file_name, self.data)

    def read(self, key):
        """
        :type key: str
        :return: any value
        """
        if key in self.data.keys():
            return self.data[key]
        else:
            return None

    def delete(self, key):
        """
        :type key: str
        """
        if key in self.data.keys():
            del self.data[key]
            io.savemat(Config.local_data_file_name, self.data)

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
        self.frequency = 0.
        self.blog_url = Config.blog_url + '{}/description'.format(self.title.lower().replace(' ', '-'))
        
        # solution url
        self.python = ''

    def write_description(self, f):
        """
        capture the problem's description from a website
        and write it into a md file.
        """
        target = self.blog_url
        request = requests.get(url = target)
        html = request.text
        div_bf = BeautifulSoup(html, features="lxml")
        div = div_bf.find_all('div', class_ = 'markdown-body')
        p_bf = BeautifulSoup(str(div[0]), features="lxml")
        p = p_bf.find_all(['p','pre'])

        for i, item in enumerate(p):
            for value in item.contents:
                # convert to value from tag
                value = str(value)
                if i > 0:
                    # reformat examples section
                    value = value.replace('\r\n', '')
                    value = value.replace('<b>Output', '  \n<b>Output')
                    value = value.replace('<strong>Output', '  \n<strong>Output')
                    # sometimes it would miss <code> syntax on both sides of a list
                    if value.find(' [') != -1:
                        value = value.replace(' [', ' <code>[')
                        value = value.replace('] ', ']</code>')
                        value = value.replace('].', ']</code>.')
                    
                f.write(value)
            f.write('\n\n')

    def write_frequency(self, f):
        """
        capture the problem's frequency from a website
        and display it as emoji in a md file.
        """
        target = Config.blog_search_url + self.id_
        request = requests.get(url = target)
        html = request.text
        div_bf = BeautifulSoup(html, features="lxml")
        div = div_bf.find_all('div', class_ = 'progress-bar progress-bar-success')
        self.frequency = float(div[0].get('aria-valuenow')) / float(div[0].get('aria-valuemax')) * 10
        for i in range(10):
            if i <= self.frequency + 1:
                f.write(':fire:')
            else:
                f.write(':snowflake:')
        f.write('\n\n')

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

class Markdown:
    """
    Generate Markdown file for a problem.
    """

    def __init__(self, id_):
        """
        :param id_: problem number
        """
        self.id_ = id_

        # initial problem's attributes
        table_instance = TableContent().get_leetcode_problems()
        self.item = table_instance[self.id_]
        self.title = self.item.title
        self.url = self.item.url
        self.lock = self.item.lock
        self.difficulty = self.item.difficulty
        
    def create_markdown(self):
        """
        create the markdown file.
        """
        file_path = Config.local_path + '/pending/' + self.id_ + '. ' + self.title + '.md'
        with open(file_path, 'w') as f:
            f.write('# ' + self.id_ + '. ' + self.title + '\n\n')
            f.write('## Tags\n\n')
            f.write('- ' + self.lock + '\n')
            f.write('- ' + self.difficulty + '\n')
            f.write('- Frequency: ')
            self.item.write_frequency(f)
            f.write('## Links\n\n')
            f.write('[Leetcode]({})\n\n'.format(self.url))
            f.write('[Blog]({})\n\n'.format(self.item.blog_url))
            f.write('## Description\n\n')
            self.item.write_description(f)
            f.write('## Python code\n\n')
            f.write('```python\n\n' + '```\n\n')
            f.write('## Visualization\n\n' + Config.holder_gif + '\n\n')
            f.write('## Reference\n\n' + 'None\n')

class Gifs:
    '''
    used to attach new existed gifs to corresponding md files
    '''

    def __init__(self):
        # store the file name of all processed gifs
        data = Data()
        self.existed_gifs = data.read('gifs')
        self.all_gifs = os.listdir(Config.local_gifs_path)

    def list_of_new_gifs(self):
        '''
        return a list contains all new existed gif's file names
        '''
        result = self.all_gifs
        data = Data()
        data.write('gifs', result)
        if self.existed_gifs:
            for i in self.existed_gifs:
                result.remove(i)
        return result

    def write_new_gifs_to_files(self):
        '''
        write the url of all new gifs to corresponding files
        '''
        for i in self.list_of_new_gifs():
            file_path = Config.local_pending_path + i.replace('.gif', '.md')
            data = ''
            with open(file_path, 'r+') as f:
                for line in f.readlines():
                    if (line.find(Config.holder_gif) == 0):
                        url = Config.github_gif_url + i.replace(' ', '%20')
                        line = '![gif]({})\n'.format(url)
                    data += line
            with open(file_path, 'r+') as f:
                f.writelines(data)

def main():
    id_ = input("Problem Number (or type 'gif' to insert gif url): ")
    if id_ == 'gif':
        gifs = Gifs()
        gifs.write_new_gifs_to_files()
    else:
        Markdown(id_).create_markdown()

if __name__ == '__main__':
    main()