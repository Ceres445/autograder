import csv
import json
import os
import subprocess
import sys

# To call this script from the command line, run this:
# python3 autograder.py <path_of_c_code_file> <path_of_testcase_json_file> -flag
# use the -i flag to operate in instructor mode
# use the -t flag to operate in testcase generator mode

# To call this script in the batch processing mode, use:
# python3 autograder.py <path_of_testcase_json_file> -b


def autoeval(code_path, testcases_path, flag=None) -> tuple:
    score = 0
    testcase_num = 0
    output = ""

    # Batch processing mode
    # currently appends new entry to end of csv, and doesn't make a new csv if it already exists
    # Loads testcases from the json file as a python dict

    with open(testcases_path, "r") as f:
        testcases = json.load(f)

    # Prints code file name
    output += (
        "Testing code for student with BITS ID: "
        + os.path.splitext(os.path.basename(code_path))[0]
        + "\n"
    )

    # Compiles C code
    # Compilation errors need to be handled here
    compilation_process = subprocess.run(
        "gcc " + code_path + " -o /tmp/a.out",
        text=True,
        timeout=5,
        shell=True,
        capture_output=True,
    )

    if not os.path.exists(
        os.path.join("/tmp/a.out")
    ):  # If compilation error occurs
        output += "Compilation Error:\n"
        print(compilation_process.stderr)
        return output, 0  # Exit if compilation error in student mode

    for test in testcases["test_cases"]:
        testcase_num += 1
        # Returns CompletedProcess instance with attributes args, returncode, stdout and stderr, all of type string.
        process_stdin = test["input"]

        try:
            # Student mode
            output += "-----TEST CASE NUMBER " + str(test["id"]) + "-----\n"
            output += "---Given Input---\n"
            output += test["input"] + "\n"
            output += "---Expected Output---"
            output += test["output"] + "\n"
            output += "---Your Output---"

            # Terminate process after 5 seconds
            completed_process = subprocess.run(
                "/tmp/a.out",
                capture_output=True,
                input=process_stdin,
                text=True,
                timeout=test["time_out"],
                shell=True,
                check=False,
            )

            process_stdout = completed_process.stdout

        except subprocess.TimeoutExpired:
            # Student mode or Test Case Generator mode
            output += "Timeout on test case " + str(test["id"]) + "\n"
            output += "---Result: Failed---" + "\n"

        except subprocess.CalledProcessError as error:
            # Student mode and Test Case Generator mode
            output += ("Exception: ", error.stderr + "\n")
            output += "---Result: Failed---" + "\n"

        except Exception as error:
            # All other exceptions
            # Unlikely that any exceptions other than timeout or runtime errors occur, but this handles it
            if flag == None or flag == "-t":
                # Student mode and Test Case Generator mode
                output += "Exception:" + str(error) + "\n"
                output += "---Result: Failed---" + "\n"

        else:

            testcase_passed = process_stdout == test["output"]
            output += process_stdout + "\n"
            result = "Passed" if process_stdout == test["output"] else "Failed" 
            output += "---Result: " + result + "---" + "\n"

            # Increases score if stdout and expected output match
            score += int(testcase_passed)

    output += "\nFinal Score:" + str(score) + "/" + str(testcase_num)

    # Deletes a.out after evaluation
    if os.path.exists("/tmp/a.out"):
        os.remove("/tmp/a.out")

    return output, score
