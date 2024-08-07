import os
import sys
import time
import urllib.request
import uuid

import lxml.etree
import requests
from prettytable import PrettyTable

from ..dispatch import FormatText, get_arguments, get_logging
from ..dispatch.dispatch_globals import (
    ARTIFACT_BASE_URL,
    TESTING_FARM_ENDPOINT,
    LATEST_TASKS_FILE,
    DEFAULT_TASKS_FILE,
    C2R_COMPOSE_MAPPING,
)

ARGS = get_arguments()
RETURN_VALUE = None
"""
 0 - All pass
 1 - Python exception or bailout
 2 - No error at least one fail
 3 - At least one error
 4 - No result
 everything else - consult with Tesar maintainer(s)
"""
ALL_PASS = 0
FAIL_HERE = 2
ERROR_HERE = 3
NO_RESULT = 4

LOGGER = get_logging()


def update_retval(new_value):
    global RETURN_VALUE
    if RETURN_VALUE is None or new_value > RETURN_VALUE:
        RETURN_VALUE = new_value


def parse_tasks():
    request_url_list = []
    tasks_source = None
    if ARGS.latest:
        if os.path.exists(LATEST_TASKS_FILE):
            tasks_source = LATEST_TASKS_FILE
            tasks_source_data = open(tasks_source).readlines()
        else:
            LOGGER.critical(
                f"The path to the latest jobs file {LATEST_TASKS_FILE} does not exist!"
            )
            LOGGER.critical(
                f"Do not use --latest option if you wish to parse values of the default {DEFAULT_TASKS_FILE} path."
            )
            LOGGER.critical(
                "Or use the --file option with path to a file containing the job IDs."
            )
            sys.exit(1)
    elif ARGS.file:
        tasks_source = ARGS.file
        tasks_source_data = []
        for file in tasks_source:
            if os.path.exists(file):
                task_ids = open(file).readlines()
                tasks_source_data.extend(task_ids)
            else:
                LOGGER.critical(f"Given path {ARGS.file} does not exist!")
                sys.exit(1)
    elif ARGS.cmd:
        tasks_source_data = ARGS.cmd
    else:
        if os.path.exists(DEFAULT_TASKS_FILE):
            tasks_source = DEFAULT_TASKS_FILE
            tasks_source_data = open(tasks_source).readlines()
        else:
            LOGGER.critical(f"The default file containing tasks doesn't exist.")
            LOGGER.critical(
                f"Pass the job IDs with the --cmd option or create and feed the {DEFAULT_TASKS_FILE} with job IDs."
            )
            sys.exit(1)

    for task in tasks_source_data:
        task = task.strip().rstrip("/")

        if not task:
            continue
        elif task.startswith(TESTING_FARM_ENDPOINT):
            task = task
        elif task.startswith(ARTIFACT_BASE_URL):
            task = task.replace(ARTIFACT_BASE_URL, TESTING_FARM_ENDPOINT)
        else:
            try:
                task = TESTING_FARM_ENDPOINT + "/" + str(uuid.UUID([part for part in task.split('/') if part][-1]))
            except ValueError:
                LOGGER.warning(f"Unrecognized task {task}")
                update_retval(NO_RESULT)
                continue

        # Validate UUID
        try:
            task_id = task.split("/")[-1]
            uuid.UUID(task_id)
        except ValueError:
            raise ValueError(task_id)

        request_url_list.append(task)

    return request_url_list, tasks_source


def parse_request_xunit(request_url_list=None, tasks_source=None, skip_pass=False):
    logs_base_directory = "/var/tmp/tesar/logs"

    if request_url_list is None or tasks_source is None:
        request_url_list, tasks_source = parse_tasks()
    if len(request_url_list) == 0 or all(element == "" for element in request_url_list):
        LOGGER.critical("There are no tasks to report for.")
        LOGGER.critical(
            f"Verify the {tasks_source} has at least one task in it or pass the values to the commandline with -c/--cmd."
        )
        sys.exit(1)

    parsed_dict = {}
    clear_line = "\x1b[2K"
    spacer = " " * 10
    loading_chars = ["/", "-", "\\", "|"]
    index = 0

    LOGGER.info("Reporting for the requested tasks:")
    for url in request_url_list:
        LOGGER.debug(f"Getting results of '{url}'")
        request = requests.get(url)
        request_state = request.json()["state"].upper()
        request_uuid = request.json()["id"]
        request_target = request.json()["environments_requested"][0]["os"]["compose"]
        request_arch = request.json()["environments_requested"][0]["arch"]
        request_datetime_created = request.json()["created"]
        request_datetime_parsed = request_datetime_created.split(".")[0]
        request_plan = request.json()["test"]["fmf"]["name"] or ""

        log_dir = f"{request_uuid}_logs"

        if request_state == "COMPLETE":
            request_state = FormatText.bg_green + request_state + FormatText.bg_default
        elif request_state == "QUEUED":
            request_state = FormatText.bg_blue + request_state + FormatText.bg_default
        elif request_state == "RUNNING":
            request_state = FormatText.bg_cyan + request_state + FormatText.bg_default
        elif request_state == "ERROR":
            request_state = FormatText.bg_yellow + request_state + FormatText.bg_default
            update_retval(ERROR_HERE)

        compose_len = _eval_longest_compose()

        LOGGER.info(
            f"{FormatText.bold}{FormatText.blue}{str(request_target):<{compose_len}} {request_plan:<20}{FormatText.end} {url} {request_state}"
        )

        if ARGS.wait:
            while request.json()["state"] not in ("complete", "error", "canceled"):
                print(end=clear_line)
                print(
                    f"Waiting for the job to finish.{spacer}{loading_chars[index]}",
                    end="\r",
                    flush=True,
                )
                index = (index + 1) % len(loading_chars)
                time.sleep(30)
                request = requests.get(url)
            else:
                LOGGER.info("Job finished!")
        else:
            if (
                request.json()["state"] != "complete"
                and request.json()["state"] != "error"
            ):
                LOGGER.warning(
                    f"Request {url} is still running, wait for it to finish or use --wait."
                )
                LOGGER.info("Skipping to the next request.")
                print("\n")
                update_retval(NO_RESULT)
                continue

        request_summary = request.json()["result"]["summary"]
        request_result_overall = request.json()["result"]["overall"]
        if request.json()["state"] == "error":

            error_formatted = FormatText.bg_red + "ERROR" + FormatText.bg_default
            error_reason = request_summary
            message = (
                f"Request ended up in {error_formatted} state, because {error_reason}.\n"
                f"See more details on the result page {url.replace(TESTING_FARM_ENDPOINT, ARTIFACT_BASE_URL)}"
            )
            LOGGER.critical(FormatText.bold + message + FormatText.end)
            update_retval(ERROR_HERE)
            # NOTE(ivasilev) There is a way to retrieve results even when the xunit file is not there, so let's not
            # skip tests processing upon error. Kudos to mmacura.

        xunit = request.json()["result"]["xunit"]
        # TODO(mmacura): possibly always use artifacts/results.xml url instead of xunit in the TF endpoint
        if not xunit:
            results_xml_url = request.json()["result"]["xunit_url"]
            results_xml_response = requests.get(results_xml_url)
            if results_xml_response:
                xunit = results_xml_response.text
            else:
                LOGGER.critical("Unable to find the xml to parse.")
                LOGGER.critical("Trying to fall back to the request results.")
                if request_result_overall and request_summary:
                    LOGGER.info(
                        f"Result: {FormatText.bold}{request_result_overall}{FormatText.end}"
                    )
                    LOGGER.info(
                        f"Summary: {FormatText.bold}{request_summary}{FormatText.end}"
                    )
                else:
                    LOGGER.info("Couldn't find any valuable information.")
                    LOGGER.info(f"Please consult with {url}")
                update_retval(ERROR_HERE)
                continue

        xml = lxml.etree.fromstring(xunit.encode())

        job_result_overall = xml.xpath("/testsuites/@overall-result")[0]
        job_test_suite = xml.xpath("//testsuite")

        # If there is just a single test suite returned and the name of the test suite
        # is pipeline, we can assume that the response contains only information about the pipeline.
        # Set the potential_pipeline_error to True and hand over to the overall job result evaluation
        potential_pipeline_error = False
        if (
            len(job_test_suite) == 1
            and job_test_suite[0].xpath("./@name")[0] == "pipeline"
        ):
            potential_pipeline_error = True

        if job_result_overall == "passed":
            update_retval(ALL_PASS)
        elif job_result_overall == "failed":
            update_retval(FAIL_HERE)
        elif job_result_overall == "error":
            update_retval(ERROR_HERE)
            # Bail out, when the potential pipeline error assessment returns True
            if potential_pipeline_error:
                LOGGER.critical(
                    f"Potential pipeline ERROR, please verify the accuracy of the assessment at {url}"
                )
                LOGGER.critical(f"Result summary: {request_summary}")
                continue
        else:
            update_retval(99)

        if skip_pass and job_result_overall.upper() == "PASSED":
            LOGGER.debug(f"Skipping '{url}' as the overall result is pass")
            continue

        if ARGS.download_logs:
            LOGGER.info("  > Downloading the log files.")
            # Create the log directory path for the request
            log_dir_path = os.path.join(logs_base_directory, log_dir)
            os.makedirs(log_dir_path, exist_ok=True)

        if request_uuid not in parsed_dict:
            parsed_dict[request_uuid] = {
                "target_name": request_target,
                "testsuites": [],
            }

        for elem in job_test_suite:
            testsuite_testcase = elem.xpath("./testcase")
            # With the latest Testing Farm release, the testsuite name does not include the target name
            # it consist of only the plan name
            testsuite_name = elem.xpath("./@name")[0].split(":")[-1]
            try:
                testsuite_arch = elem.xpath(
                    "./testing-environment/property[@name='arch']/@value"
                )[0]
            except IndexError:
                testsuite_arch = elem.xpath("./@name")[0].split(":")[-1]
            testsuite_result = elem.xpath("./@result")[0].upper()
            testsuite_test_count = elem.xpath("./@tests")
            testsuite_log_dir = testsuite_name.split("/")[-1]
            LOGGER.debug(f"Processing results of testsuit '{testsuite_name}'")

            if skip_pass and testsuite_result == "PASSED":
                LOGGER.debug(
                    f"Skipping testsuite '{testsuite_name}' as the result is pass"
                )
                continue

            testsuite_data = {
                "testsuite_name": testsuite_name,
                "testsuite_arch": testsuite_arch,
                "testsuite_result": testsuite_result,
                "testcases": [],
            }
            parsed_dict[request_uuid]["testsuites"].append(testsuite_data)

            if ARGS.download_logs:
                # Create the log directory path for the testsuite
                testsuite_log_dir_path = os.path.join(log_dir_path, testsuite_log_dir)
                os.makedirs(testsuite_log_dir_path, exist_ok=True)

            for test in testsuite_testcase:
                testcase_name = test.xpath("./@name")[0]
                testcase_result = test.xpath("./@result")[0].upper()
                LOGGER.debug(
                    f"Processing result of test '{testsuite_name}/{testcase_name}'"
                )
                if skip_pass and testcase_result == "PASSED":
                    LOGGER.debug(
                        f"Skipping test '{testsuite_name}/{testcase_name}' as the result is pass"
                    )
                    continue
                testcase_log_url = test.xpath('./logs/log[@name="testout.log"]/@href')[
                    0
                ]
                log_name = f"{request_target}_{testcase_name.split('/')[-1]}.log"

                # Constructing the parsed dictionary
                testcase_data = {
                    "testcase_name": testcase_name,
                    "testcase_result": testcase_result,
                }
                testsuite_data["testcases"].append(testcase_data)

                if ARGS.download_logs:
                    response = urllib.request.urlopen(testcase_log_url)
                    log_data = response.read().decode("utf-8")
                    log_file_path = os.path.join(testsuite_log_dir_path, log_name)

                    with open(log_file_path, "w") as logfile:
                        logfile.write(log_data)

        if ARGS.download_logs:
            LOGGER.info(f"    > Logfiles stored in {log_dir_path}")

    return parsed_dict


def _split_name(name, index):
    """A helper that splits a test name at the position given by index"""
    name_raw = name.split("/")
    try:
        name_raw.remove("")
    except ValueError:
        pass
    return "/".join(name_raw[index:])


def build_table_comparison():
    """
    Generate a table holding comparable results of several tests.

    This allows a clear comparison of several tft runs with particular test
    results side by side in respectable columns.
    Sample format:
    **     tft_run_uuid1  tft_run_uuid2
    test1   PASS            FAIL
    test2   -               PASS
    test3   PASS            PASS
    """
    planname_split_index = 0
    testname_split_index = 0
    if ARGS.short:
        planname_split_index = -1
        testname_split_index = -1
    if ARGS.split_testname:
        testname_split_index = ARGS.split_testname
    if ARGS.split_planname:
        planname_split_index = ARGS.split_planname

    parsed_dict = parse_request_xunit(skip_pass=ARGS.skip_pass)
    result_table = PrettyTable()
    uuids = list(parsed_dict.keys())
    fields = ["Test Plan"] + uuids
    result_table.field_names = fields
    # plan_name -> uuid run result for particular plan
    regroup_results_plans = {}
    # plan_name -> test_name -> uuid run result for particular test
    regroup_results_tests = {}
    unified_names_map = {}
    for plan_name in ARGS.unify_results or []:
        name1, name2 = plan_name.split("=", 2)
        unified_names_map[name1] = plan_name
        unified_names_map[name2] = plan_name

    def _get_plan_key(testsuite_data):
        plan_key = _split_name(testsuite_data["testsuite_name"], planname_split_index)
        # check against unifed map to combine results
        return unified_names_map.get(plan_key) or plan_key

    for task_uuid, data in parsed_dict.items():
        for testsuite_data in data["testsuites"]:
            res_uuid = {
                "result": testsuite_data["testsuite_result"],
                "testcases": sorted(
                    (x for x in testsuite_data["testcases"]),
                    key=lambda x: x["testcase_name"],
                ),
            }
            plan_key = _get_plan_key(testsuite_data)
            try:
                regroup_results_plans[plan_key][task_uuid] = res_uuid
            except KeyError:
                regroup_results_plans[plan_key] = {task_uuid: res_uuid}
            # Preparation for plans -> tests mapping
            if plan_key not in regroup_results_tests:
                regroup_results_tests[plan_key] = {}
            # Now process testcases for easier level2 table processing
            for testcase_data in testsuite_data["testcases"]:
                plan_key = _get_plan_key(testsuite_data)
                test_key = _split_name(
                    testcase_data["testcase_name"], testname_split_index
                )
                if test_key not in regroup_results_tests[plan_key]:
                    regroup_results_tests[plan_key][test_key] = {}
                try:
                    regroup_results_tests[plan_key][test_key][
                        task_uuid
                    ] = testcase_data["testcase_result"]
                except KeyError:
                    regroup_results_tests[plan_key][test_key] = {
                        task_uuid: testcase_data["testcase_result"]
                    }

    for plan_name, plan_data in regroup_results_plans.items():
        if ARGS.level2:
            # Append first row with plan name only
            result_table.add_row([plan_name] + [""] * len(uuids))
            result_table.add_row(["*"] + [""] * len(uuids))
            for test_name, test_data in regroup_results_tests[plan_name].items():
                row_data = [f'{"*" * 4} {test_name}']
                for uuid in uuids:
                    row_data.append(colorize(test_data.get(uuid, "-")))
                result_table.add_row(row_data)
        else:
            row_data = [plan_name]
            for uuid in uuids:
                # Report just plans
                if not uuid in plan_data:
                    # this plan has not been executed for this run
                    row_data.append("-")
                else:
                    row_data.append(colorize(plan_data[uuid]["result"]))
            result_table.add_row(row_data)
    result_table.align = "l"

    return result_table


def build_table():
    parsed_dict = parse_request_xunit(skip_pass=ARGS.skip_pass)

    result_table = PrettyTable()
    # prepare field names
    fields = []
    fields += ["UUID", "Target"]
    if ARGS.showarch:
        fields += ["Arch"]
    fields += ["Test Plan"]
    if ARGS.level2:
        fields += ["Test Case"]
    fields += ["Result"]
    result_table.field_names = fields

    color_format_default = FormatText.end

    planname_split_index = 0
    testname_split_index = 0

    if ARGS.short:
        planname_split_index = -1
        testname_split_index = -1

    if ARGS.split_testname:
        testname_split_index = ARGS.split_testname

    if ARGS.split_planname:
        planname_split_index = ARGS.split_planname

    def _gen_row(uuid="", target="", arch="", testplan="", testcase="", result=""):
        if "UUID" in fields:
            yield uuid
        if "Target" in fields:
            yield target
        if "Arch" in fields:
            yield arch
        if "Test Plan" in fields:
            yield testplan
        if "Test Case" in fields:
            yield testcase
        if "Result" in fields:
            yield result

    def add_row(*args, **kwargs):
        result_table.add_row(tuple(_gen_row(*args, **kwargs)))

    for task_uuid, data in parsed_dict.items():
        add_row(task_uuid, data["target_name"])
        last_arch = None
        for testsuite_data in data["testsuites"]:
            if last_arch != testsuite_data["testsuite_arch"] and "Arch" in fields:
                last_arch = testsuite_data["testsuite_arch"]
                add_row(arch=last_arch)
            testsuite_result = testsuite_data["testsuite_result"]
            add_row(
                testplan=colorize(
                    testsuite_result,
                    _split_name(testsuite_data["testsuite_name"], planname_split_index),
                ),
                result=colorize(testsuite_result),
            )
            if "Test Case" in fields:
                for testcase in testsuite_data["testcases"]:
                    testcase_result = testcase["testcase_result"]
                    add_row(
                        testcase=colorize(
                            testcase_result,
                            _split_name(
                                testcase["testcase_name"], testname_split_index
                            ),
                        ),
                        result=colorize(testcase_result),
                    )

    result_table.align = "l"

    return result_table


def get_color_format(result):
    color_format_default = FormatText.end
    if result == "PASSED":
        return FormatText.green
    elif result == "FAILED":
        return FormatText.red
    elif result == "ERROR":
        return FormatText.yellow
    return color_format_default


def colorize(result, label=None, color_format_default=FormatText.end):
    """
    Colorize provided label (or result) using color associated to the provided result.

    :return: Colorized label (if provided) or result (if label is not provided)
    :rtype: str
    """
    label = label if label else result
    return get_color_format(result) + label + color_format_default


def _eval_longest_compose():
    """
    Helper function evaluating the longest compose name in the mapping.
    Returns len int of the longest.
    """
    compose_len = 0
    for nest_dict in C2R_COMPOSE_MAPPING.values():
        eval_compose_len = len(nest_dict.get("compose"))
        if eval_compose_len > compose_len:
            compose_len = len(nest_dict.get("compose"))

    compose_len = compose_len + 5

    return compose_len


def main(result_table=None):
    if result_table is None:
        result_table = build_table_comparison() if ARGS.compare else build_table()
    if result_table.rowcount > 0:
        print(result_table)
    else:
        LOGGER.info("Nothing to report!")
    return RETURN_VALUE
