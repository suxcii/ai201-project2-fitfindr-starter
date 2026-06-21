from tools import search_listings

# Test 1: should find results
results = search_listings('vintage graphic tee', size='M', max_price=30)
print('Test 1 results:', len(results))
if results:
    print('Top result:', results[0]['title'], '-', results[0]['price'])

# Test 2: should return empty list (impossible search)
results2 = search_listings('designer ballgown', size='XXS', max_price=5)
print('Test 2 results:', len(results2))
print('Empty list?', results2 == [])