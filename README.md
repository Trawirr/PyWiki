# PyWiki
A bot written in Python for wikipedia game of starting with a random wiki article and reaching a given one via hyperlinks

# Interesting results
Reaching 'Adolf Hitler' in 7 moves starting with Belgian Anime coonvention:
1. Fantasy Anime Comics Toys Space - 19 links
2. MCM London Comic Con - 368 links
3. Elizabeth Maxwell - 82 links
4. Overlord (novel series) - 294 links
5. Hachette Book Group - 215 links
6. The New York Times - 1227 links
7. The Holocaust - 3002 links
8. Adolf Hitler - 2620 links

# Comparison of two methods
There is possibility to train bot by letting it play game n times and remember series of articles that lead to given one and have more hyperlinks than given threshold. Bot can play the game with two modes:
- random ('r') - default mode, checks if there is a hyperlink to the given article within a set of all hyperlinks in current article, otherwise picks at random.
- better ('b') - memory based method, makes use of two text files that were created during training, checks if there is a hyperlink to any remembered article.

'better' mode is usually about 5-40 times faster than 'random' mode.

This is time comparison of these two methods below:
![plot1](https://github.com/Trawirr/PyWiki/blob/main/myplot.png)
![plot2](https://github.com/Trawirr/PyWiki/blob/main/myplot2.png)
