#!/usr/bin/python

import os, sys, re, operator, math
from bs4 import BeautifulSoup

path = os.path.dirname(os.path.realpath(__file__))

pages = 15040
#pages = 100

nodes = {}
edges = {}
users = {}
recipes = {}
index = 1
dups = 0


regex_div = re.compile('recipe_(.*)')
regex_a = re.compile('\/recipes\/(.*)')

def recipes_filter(tag):
  return tag.name == 'div' and tag.has_attr('id') and re.match(regex_div, tag.get('id'))


def is_div(n):
  return n.name == 'div' and n.get('class')

def is_span(n):
  return n.name == 'span' and n.get('class')

def is_use_count(n):
  return is_span(n) and n.get('class')[0] == 'recipe-desc__stats_item__use-count__number'

def is_fav_count(n):
  return is_span(n) and n.get('class')[0] == 'stats_item__favorites-count__number'


def parse(page):
  global index
  global dups
  soup = BeautifulSoup(open('%s/data/ifttt_%05d.html' % (path, page)))
  #print soup.head
  tags = soup.find_all(recipes_filter)
  for tag in tags:
    title = ""
    recipe_trigger = ""
    recipe_action = ""
    user = ""
    adds = 0
    favs = 0
    match = re.match(regex_div, tag.get('id'))
    id = int(match.group(1))
    for child in tag.descendants:
      if child.name == 'a' and re.match(regex_a, child.get('href')):
        if child.get('data-track-event'):
          title = child.text
        else:
          for t in child.descendants:
            if is_span(t) and t.get('class')[0] == 'recipe_trigger' and t.get('title'):
              recipe_trigger = t.get('title')
            if is_span(t) and t.get('class')[0] == 'recipe_action' and t.get('title'):
              recipe_action = t.get('title')
      elif is_div(child) and child.get('class')[0] == 'recipe-desc':
         for t in child.descendants:
           if is_div(t) and t.get('class')[0] == 'recipe-desc_creation':
             user = t.find('a').text
             break
      elif is_use_count(child):
         for t in child.descendants:
           if is_span(t) and t.get('class')[0] == 'full_value':
             adds = int(t.text.strip())
             break
      elif is_fav_count(child):
         for t in child.descendants:
           if is_span(t) and t.get('class')[0] == 'full_value':
             favs = int(t.text.strip())
             break
    
    if recipes.has_key(id):
      dups += 1 # Duplicate recipe, skip
      continue
    else:
      recipes[id] = {'title':title, 'adds':adds, 'favs':favs,\
        'trigger':recipe_trigger, 'action':recipe_action}
 
    if nodes.has_key(recipe_trigger):
      nodes[recipe_trigger]['trigger'] += 1
      nodes[recipe_trigger]['count'] += 1      
    else:
      nodes[recipe_trigger] = {'id':index, 'count':1, 'action':0, 'trigger':1}
      index += 1
    if nodes.has_key(recipe_action):
      nodes[recipe_action]['action'] += 1
      nodes[recipe_action]['count'] += 1      
    else:
      nodes[recipe_action] = {'id':index, 'count':1, 'action':1, 'trigger':0}
      index += 1

    link = recipe_trigger + '|' + recipe_action # directed edge
    if edges.has_key(link):
      edges[link]['count'] += 1
      edges[link]['recipes'].append(id)
    else:
      edges[link] = {'id':index, 'count':1, 'recipes':[id]}
      index += 1
    
    if users.has_key(user):
      users[user]['count'] += 1
      users[user]['recipes'].append(id) 
    else:
      users[user] = {'count':1, 'recipes':[id]}
    #print "[%d] %s | '%s' --> '%s' | %s | adds:%d favs:%d" % (id, title, recipe_trigger, recipe_action, person, adds, favs)
  

for x in range(1, pages+1):
  parse(x)


print "duplicates found: %d" % dups

'''
Write user stats to file
'''

n_services = 0
max_services = -1
max_recipes = -1
recipes_per_service_sum = 0

sorted_users = sorted(users.items(), key=lambda x: x[1]['count'])
sorted_users.reverse()

f = open('%s/user_stats.txt' % path,'w')

for u in sorted_users:
  n_adds = 0
  n_favs = 0

  services = {}
  for r in u[1]['recipes']:
    services[recipes[r]['trigger']] = 1
    services[recipes[r]['action']] = 1
    n_adds += recipes[r]['adds']
    n_favs += recipes[r]['favs']

  n_user_services = len(services)
  #if n_user_services == 1:
  #  print u
  u[1]['services'] = n_user_services
  n_services += n_user_services
  if n_user_services > max_services:
    max_services = n_user_services

  n_recipes = u[1]['count']
  if max_recipes < n_recipes: max_recipes = n_recipes
  recipes_per_service_sum += n_recipes / float(n_user_services)

  line = 'user:"%s" adds:%d favs:%d recipes:%s recipes_per_service:%0.2f services:%d' % \
    (u[0], n_adds, n_favs, n_recipes, n_recipes / float(n_user_services), n_user_services)

  ss = ""
  for s,t in services.iteritems():
    if len(ss): ss += ","
    ss += s
  line += ' "%s"\n' % ss
  f.write(line)

f.close()

f = open('%s/user_summary.txt' % path,'w')
n_users = len(users)
mean_services = n_services / n_users
res = "users:%d max_recipes:%d mean_services:%d max_services:%d mean_recipes_per_service:%0.2f" % \
  (n_users, max_recipes, mean_services, max_services, recipes_per_service_sum/float(n_users))
print res
f.write(res + "\n")
f.close()

service_use_count = [0]*(max_services+1)
for u in sorted_users:
  service_use_count[u[1]['services']] += 1

f = open('%s/user_services_hist.txt' % path,'w')
for i in range(1,max_services+1):
  f.write("%d %d\n" % (i, service_use_count[i]))
f.close()


'''
Write recipes stats to file
'''

sorted_recipes = sorted(recipes.items(), key=lambda x: x[1]['adds'])
sorted_recipes.reverse()
f = open('%s/recipes_stats_ordered_by_adds.txt' % path,'w')
for r in sorted_recipes:
  line = u'%d "%s" "%s" "%s" %d %d\n' % \
    (r[0], r[1]['trigger'], r[1]['action'], r[1]['title'], r[1]['adds'], r[1]['favs'])
  f.write(line.encode('utf-8'))
f.close()

sorted_recipes = sorted(recipes.items(), key=lambda x: x[1]['favs'])
sorted_recipes.reverse()
f = open('%s/recipes_stats_ordered_by_favs.txt' % path,'w')
for r in sorted_recipes:
  line = u'%d "%s" "%s" "%s" %d %d\n' % \
    (r[0], r[1]['trigger'], r[1]['action'], r[1]['title'], r[1]['adds'], r[1]['favs'])
  f.write(line.encode('utf-8'))
f.close()

'''
Write services stats to file
'''

sorted_nodes = sorted(nodes.items(), key=lambda x: x[1]['count'])
sorted_nodes.reverse()
f = open('%s/services_stats_used.txt' % path,'w')
for n in sorted_nodes:
  f.write("%s %d %d %d\n" % (n[0], n[1]['count'], n[1]['trigger'], n[1]['action']))
f.close()

sorted_nodes = sorted(nodes.items(), key=lambda x: x[1]['trigger'])
sorted_nodes.reverse()
f = open('%s/services_stats_trigger.txt' % path,'w')
for n in sorted_nodes:
  f.write("%s %d %d %d\n" % (n[0], n[1]['count'], n[1]['trigger'], n[1]['action']))
f.close()

sorted_nodes = sorted(nodes.items(), key=lambda x: x[1]['action'])
sorted_nodes.reverse()
f = open('%s/services_stats_action.txt' % path,'w')
for n in sorted_nodes:
  f.write("%s %d %d %d\n" % (n[0], n[1]['count'], n[1]['trigger'], n[1]['action']))
f.close()


'''
Write graph to file
'''

for k,v in edges.iteritems():
  n_adds = 0
  n_favs = 0
  for r in v['recipes']:
    n_adds += recipes[r]['adds']
    n_favs += recipes[r]['favs']
  popularity = max(n_adds, v['count'])
  edges[k]['adds'] = n_adds
  edges[k]['favs'] = n_favs
  edges[k]['popularity'] = popularity


header = \
'''graph
[
  Creator Gephi
  directed 1
'''
footer = '''
]'''

gml = open('%s/ifttt_use.gml' % path,'w')
gml.write(header)

sorted_nodes = sorted(nodes.items(), key=lambda x: x[1]['id'])

for n in sorted_nodes:
  gml.write('''
  node
  [
    id %d
    label "%s"
    count %d
    trigger %d
    action %d
  ]''' % (n[1]['id'], n[0], n[1]['count'], n[1]['trigger'], n[1]['action']))

for k,v in edges.iteritems():
  n = k.split('|')
  src = nodes[n[0]]['id']
  target = nodes[n[1]]['id']
  weight = math.log(v['popularity']) + 1.0
  gml.write('''
  edge
  [
    id %d
    source %d
    target %d
    value %d
    scaled %f
    recipes %d
    adds %d
    favs %d
    label "%s"
  ]''' % (v['id'], src, target, v['popularity'], weight, v['count'], \
  v['adds'], v['favs'], str(v['popularity'])) \
  )

gml.write(footer)
gml.close()



gml = open('%s/ifttt_recipes.gml' % path,'w')
gml.write(header)

for n in sorted_nodes:
  gml.write('''
  node
  [
    id %d
    label "%s"
    count %d
    trigger %d
    action %d
  ]''' % (n[1]['id'], n[0], n[1]['count'], n[1]['trigger'], n[1]['action']))

for k,v in edges.iteritems():
  n = k.split('|')
  src = nodes[n[0]]['id']
  target = nodes[n[1]]['id']
  gml.write('''
  edge
  [
    id %d
    source %d
    target %d
    value %d
    label "%s"
  ]''' % (v['id'], src, target, v['count'], str(v['count'])) \
  )

gml.write(footer)
gml.close()



