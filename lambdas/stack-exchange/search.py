import stackexchange

if __name__ == '__main__':
    so = stackexchange.Site(stackexchange.StackOverflow)
    qs = so.search(intitle='java object equals method')

    print('I found %d results' % (len(qs)))
    for q in qs:
        print('%8d %s' % (q.id, q.title))
