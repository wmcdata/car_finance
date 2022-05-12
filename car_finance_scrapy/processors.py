# -*- coding: utf-8 -*-
__all__ = [
		'date_proc'
	]

def date_proc(ctx, values):
    spider = ctx['spider']
    print('values')
    for v in values:
        dt = spider.convertDateFormat(v, spider.event_dateformat, DEFAULT_DATEFORMAT)
        if dt is not None:
            yield dt