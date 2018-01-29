import json


# TODO's:
#   - How do we mark a resource as exempt from a test? Where is this data stored?
#   - Need to add region (also needed in JSON service report)


# sort by test name
# for each test, create a list of fails, a list of warns, a list of passing and a list of errs as a markdown doc
# Options:
#   - to only list fails
#   - add checkboxes next to each test failure (for creating github issues)
#   - CSV instead of markdown

def extract_resource_name(name):
    # "test_something[resource-name]" -> "resource-name"
    return name.split("[")[-1][0:-1]

service_report = json.loads(open('cs-stage-service-report.json', 'r').read())

#{'test_name': [results], ____}
test_results = {
    k: [] for k in set([r['test_name'] for r in service_report['results']])
}

for result in service_report['results']:
    test_results[result['test_name']].append(result)

print("# AWS pytest-services results\n")
print("#### Result Meanings: TODO\n")
print("#### Jump to test\n")
tests_with_failures = []
for test in test_results:
    if len([r for r in test_results[test] if r['status'] == 'fail']) != 0:
        tests_with_failures.append(test)
	print("- [%s](#%s)" % (test,test))
print("---\n")


for test in test_results:
    if len([r for r in test_results[test] if r['status'] == 'fail']) == 0:
        continue

    print("### %s\n\n" % test)
    print("Resource Name | Metadata")
    print("------------ | -------------")

    for result in test_results[test]:
        if result["status"] == "fail":
            print("%s | %s" % (
                extract_resource_name(result['name']),
                ''.join(["{}: {} - ".format(k,v) for k,v in result['metadata'].items()])[0:-3]
            ))

    print("\n---\n\n")
