import json
import sys
from collections import defaultdict

STATUSES_TO_LIST = ['err', 'warn', 'fail']


class ReportGenerator:

    def __init__(self, service_json):
        # {'test_name': [results], ...}
        self.test_results = defaultdict(list)

        # {'test_name_fail': 2, ...}
        self.test_status_counter = defaultdict(int)

        for result in service_json['results']:
            if result['status'] in STATUSES_TO_LIST:
                self.test_results[result['test_name']].append(result)
                self.test_status_counter[result['test_name']+"_"+result['status']] += 1

    def generate(self):
        self.print_header()
        self.print_table_of_contents()
        self.print_report()

    def print_header(self):
        print("# AWS pytest-services results\n")
        print("#### Result Meanings: TODO\n")

    def print_table_of_contents(self):
        print("#### Table of Contents\n")
        for test in self.test_results:
            print("- [%s](#%s)" % (test, test))
            for status in STATUSES_TO_LIST:
                if self.test_status_counter[test+'_'+status]:
                    print("    - [%s (%s)](#%s)" % (
                        status,
                        self.test_status_counter[test+'_'+status],
                        test+'_'+status,
                    ))
        print("---\n")

    def print_report(self):
        for test in self.test_results:
            print("### %s\n\n" % test)

            for status in STATUSES_TO_LIST:
                if self.test_status_counter[test+'_'+status]:
                    print("#### %s_%s\n\n" % (test, status))
                    print("Resource Name | Metadata")
                    print("------------ | -------------")

                    for result in self.test_results[test]:
                        if result["status"] == status:
                            print("%s | %s" % (
                                self._extract_resource_name(result['name']),
                                ''.join(["{}: {} - ".format(k, v) for k, v in result['metadata'].items()])[0:-3]
                            ))

                    print("\n\n")

            print("\n---\n\n")

    def _extract_resource_name(self, name):
        # "test_something[resource-name]" -> "resource-name"
        return name.split("[")[-1][0:-1]


if __name__ == '__main__':
    ReportGenerator(json.loads(open(sys.argv[1], 'r').read())).generate()
