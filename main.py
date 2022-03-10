import bs4
import requests
import numpy as np
import time
import matplotlib.pyplot as plt


# my list of given size with a few useful methods
class MyList:
    def __init__(self, size):
        self.size = size
        self.arr = [None for i in range(size)]

    def shift(self, n=1):
        for j in range(n):
            for i in range(self.size - 1):
                self.arr[i] = self.arr[i + 1]
            self.arr[self.size - 1] = None

    def add(self, element):
        self.shift()
        self.arr[self.size - 1] = element

    def get_scores(self):
        scores = [len(get_links(get_soup(page_base + link))) for link in self.arr]
        for i in range(self.size):
            scores[i] = scores[i] * (1.1 + i / 10)
        return scores

    def write_to_files(self, filename1, filename2, threshold):
        file1 = open(filename1, 'a')
        file2 = open(filename2, 'a')

        text = ''
        for i in range(self.size):
            print(self.size - 1 - i)
            if self.arr[self.size - 1 - i] == None:
                break
            link = page_base + self.arr[self.size - 1 - i]
            num_links = len(get_links(get_soup(link)))
            if num_links > threshold:
                file1.write(link + '\n')
                text = link + text
                file2.write(text + '\n')
            else:
                break
            text = ', ' + text
        file1.close()
        file2.close()

    def resize(self, n):
        my_list = MyList(n)
        for element in self.arr[-n:]:
            my_list.add(element)
        return my_list

    def __str__(self):
        text = ''
        for element in [n < self.size - 1 and f'{self.arr[n]}, ' or f'{self.arr[n]}' for n in range(self.size)]:
            text += element
        return text


def get_soup(link):
    page = requests.get(link)
    return bs4.BeautifulSoup(page.content, 'html.parser')


def get_links(soup, tracking=False):
    links = [link['href'][6:] for link in soup.find(id='mw-content-text').findAll('a', href=True)
             if link['href'][0:5] == '/wiki' and ':' not in link['href']]
    if tracking:
        print(f"{soup.find('title').text.replace(' - Wikipedia', '')} - {len(links)} links")
    return links


def pick_link(links, article, mode='r'):
    if article in links:
        return page_base + article, 1
    elif mode == 'b':
        for link in links:
            page = find_remembered(page_base + link, 'close.txt')
            if page is not None:
                return find_path_for_remembered(page, 'paths.txt'), 2
    return page_base + links[np.random.randint(len(links))], 0


def find_remembered(link, filename):
    file = open(filename, 'r')
    links_remembered = file.readlines()
    file.close()

    links_remembered = [l.strip() for l in links_remembered]
    if link in links_remembered:
        return link
    return None


def find_path_for_remembered(link, filename):
    file = open(filename, 'r')
    links_remembered = [row.split(', ') for row in file.readlines()]
    file.close()

    for row in links_remembered:
        row[-1] = row[-1].replace('\n', '')

    for row in links_remembered:
        if row[0] == link:
            return row


def list_analyse(my_list):
    for i in range(my_list.size):
        if my_list.arr[i] is not None and my_list.arr[i] != 'Special:Random':
            num_links = len(get_links(get_soup(page_base + my_list.arr[i])))
            print(f'[{my_list.size - i}] {my_list.arr[i]} - {num_links}')
        else:
            print(f'[{my_list.size - i}] {my_list.arr[i]}')


def go_with_path(path):
    pass


def play_wiki(article, mode='r', tracking=True, page='https://en.wikipedia.org/wiki/Special:Random', training=False, threshold=1000):
    if training:
        last_links = MyList(10)
    counter = 0
    # for tracking progress
    progress = []
    time_start = time.time()
    while True:
        if training:
            last_links.add(page.replace(page_base, ''))
        soup = get_soup(page)
        links = get_links(soup, tracking)
        page_prev = page

        title = soup.find('title').text.replace(' - Wikipedia', '')
        progress.append(title)
        page, found = pick_link(links, article, mode)
        if found == 1:
            if training:
                soup = get_soup(page)
                links = get_links(soup, tracking)
                title = soup.find('title').text.replace(' - Wikipedia', '')
                progress.append(title)
                counter += 1
            break
        elif found == 2:
            page.append(page_base + article)
            counter += len(page)
            for link in page:
                soup = get_soup(link)
                title = soup.find('title').text.replace(' - Wikipedia', '')
                progress.append(title)
                get_links(soup, tracking)
            break
        counter += 1
    full_time = time.time() - time_start
    if tracking:
        print(f'Time: {round(full_time, 2)}s, counter: {counter}, mode {mode}\n{progress}')
    if training:
        last_links.write_to_files('close.txt', 'paths.txt', threshold)
        list_analyse(last_links)
    return full_time, counter


def train(article, n, threshold):
    for m in range(n):
        play_wiki(article, training=True, threshold=threshold)


def autolabel(rects, ax):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def comparison(article, n):
    random_pages = []
    time_counter_random = []
    time_counter_better = []
    for i in range(n):
        links = get_links(get_soup(page_base + page_rand))
        random_pages.append(page_base + links[np.random.randint(len(links))])
    for random_page in random_pages:
        timer, counter = play_wiki(article, mode='r', tracking=False, page=random_page)
        time_counter_random.append([round(timer, 2), counter])
        timer, counter = play_wiki(article, mode='b', tracking=False, page=random_page)
        time_counter_better.append([round(timer, 2), counter])
    for i in range(n):
        print(f'{random_pages[i]}\n'
              f'Random: {time_counter_random[i][0]}s, {time_counter_random[i][1]} clicks \n'
              f'Better: {time_counter_better[i][0]}s, {time_counter_better[i][1]} clicks')

    labels = [p.split('/')[-1][:10] + '...' for p in random_pages]
    times_random = [x[0] for x in time_counter_random]
    times_better = [x[0] for x in time_counter_better]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, times_random, width, label='Random')
    rects2 = ax.bar(x + width / 2, times_better, width, label='Memory based')

    ax.set_ylabel('Time')
    ax.set_title('Time by method of searching')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    autolabel(rects1, ax)
    autolabel(rects2, ax)

    fig.tight_layout()
    plt.show()

page_base = 'https://en.wikipedia.org/wiki/'
page_rand = 'Special:Random'
if __name__ == '__main__':

    #train('Adolf_Hitler', 50, 1000)

    play_wiki('Adolf_Hitler', mode='b')
    #play_wiki('Adolf_Hitler', mode='r')
    comparison('Adolf_Hitler', 5)




