# -*- coding: utf-8 -*-

import bottle

bottle.debug(True)

@bottle.route('/')
def test():
    return "test"

def main():
    bottle.run(host='localhost', port=8080)

if __name__== '__main__' :
    main()
