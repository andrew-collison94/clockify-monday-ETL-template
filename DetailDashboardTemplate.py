import requests
import json
import requests.models
from itertools import chain
import config

boardName = "Sample Board Name"  # Name of linked Monday.com board
boardId = config.detailDashboardMondayBoardID  # Monday.com Board ID
# List of Monday.com columns that will be updated
columnId = config.detailDashboardMondayColumnID
expectedRowCount = 9  # Count of every row on board in Monday.com at the time of setup
workspace_id = config.workspaceConfigClockify  # Clockify Workspace ID
startdate = ["2021-10-01T00:00:00.000", "2021-11-01T00:00:00.000", "2021-12-01T00:00:00.000", "2022-01-01T00:00:00.000", "2022-02-01T00:00:00.000", "2022-03-01T00:00:00.000",
             "2022-04-01T00:00:00.000"]  # List of start dates formatted like: "2021-05-01T00:00:00.000" for Clockify query (used for rows that iterate to diplay a monthly total)
enddate = ["2021-10-31T23:59:59.999", "2021-11-30T23:59:59.999", "2021-12-31T23:59:59.999", "2022-01-31T23:59:59.999", "2022-02-28T23:59:59.999", "2022-03-31T23:59:59.999",
           "2022-04-30T23:59:59.999"]

# Clockify Project ID: Sample Clockify Project Name
project_id = "0000000000000000000"
# Admin API key linked to user: API Admin Name
apiKeyClockify = config.apiConfigClockify


urlClockify = "https://reports.api.clockify.me/v1/workspaces/{0}/reports/summary".format(
    workspace_id)
headersClockify = {"X-Api-Key": apiKeyClockify,
                   "Content-Type": "application/json"}

apiKeyMonday = config.apiConfigMonday
urlMonday = 'https://api.monday.com/v2'
headersMonday = {"Authorization": apiKeyMonday}
# Clockify Task IDs. Each group in [] represents a row in Monday.com organized from top to bottom
clockifyTaskIdList = config.detailDashboardClockifyTaskID
# Monday Item IDs. Each ID represents a row, organized from top to bottom
mondayItemIdList = config.detailDashboardMondayItemID
# clockifyTaskIdList and mondayItemIdList must contain the same amount of values
if len(mondayItemIdList) != len(clockifyTaskIdList):
    print("The number of tasks in Clockify and items in Monday do not match up, please contact an administrator")
    raise PermissionError(
        "Clockify task list and Monday item list do not contain the same amount of items")


def mondayRowCheck():

    query = f'''query($boardid:[Int]){{boards(ids: $boardid){{items {{ id }} }}}}'''
    vars = {'boardid': boardId}
    payloadRowCheck = {'query': query, 'variables': vars}
    responseRowCheck = requests.post(
        url=urlMonday, json=payloadRowCheck, headers=headersMonday)
    rowCheckTemp = responseRowCheck.json()
    rowCheck = rowCheckTemp['data']['boards'][0]['items']
    currentRowCount = len(rowCheck)
    if currentRowCount > expectedRowCount:
        print("The number of rows in ", boardName,
              " currently exceeds the program setup. Please remove inserted row or contact an administrator")
        raise PermissionError(
            "Current row count is greater than expected row count")
    if currentRowCount < expectedRowCount:
        print("The number of rows in ", boardName,
              " has dropped below the expected amount. Please replace deleted row or contact an administrator")
        raise PermissionError(
            "Current row count is lower than expected row count")


mondayRowCheck()


def financeDetail():
    for miil, ctil in zip(mondayItemIdList, clockifyTaskIdList):
        def clockify():
            totalBillHoursList = []
            for sd, ed in zip(startdate, enddate):
                payloadClockify = {
                    "dateRangeStart": sd,
                    "dateRangeEnd": ed,
                    "summaryFilter": {
                        "groups": ["PROJECT", "TASK"]},
                    "projects": {
                        "ids": [project_id]},
                    "tasks": {
                        "ids": ctil}
                }

                responseClockify = requests.post(
                    urlClockify, headers=headersClockify, data=json.dumps(payloadClockify))
                timeExtract = responseClockify.json()
                try:
                    totalBillSeconds = timeExtract['totals'][0]['totalBillableTime']
                    totalBillHours = totalBillSeconds/3600
                    totalBillHoursList.append(totalBillHours)
                except:
                    totalBillHoursList.append(0)

                if responseClockify.status_code == 401:
                    print('Status: ', responseClockify.status_code)
                    raise PermissionError(
                        "The API key for Clockify appears to be expired.")
                if responseClockify.status_code != 200:
                    print('Status: ', responseClockify.status_code)
                    raise Exception("Query failed.")
            return(totalBillHoursList)

        clockify()

        def monday():
            totalBillHoursList = clockify()
            varStringify = {
                columnId[0]: totalBillHoursList[0],
                columnId[1]: totalBillHoursList[1],
                columnId[2]: totalBillHoursList[2],
                columnId[3]: totalBillHoursList[3],
                columnId[4]: totalBillHoursList[4],
                columnId[5]: totalBillHoursList[5],
                columnId[6]: totalBillHoursList[6]}

            query = f'''mutation ($boardid: Int!, $itemid: Int!, $billable: JSON!) {{change_multiple_column_values (board_id: $boardid, item_id: $itemid, column_values: $billable) {{ id }} }}'''

            vars = {'boardid': boardId,
                    'itemid': miil,
                    'billable': json.dumps(varStringify)
                    }
            payloadMonday = {'query': query, 'variables': vars}
            responseMonday = requests.post(
                url=urlMonday, json=payloadMonday, headers=headersMonday)
            if responseMonday.status_code == 401:
                print('Status: ', responseMonday.status_code)
                raise PermissionError(
                    "The API key for Monday.com appears to be expired.")
            if responseMonday.status_code != 200:
                print('Status: ', responseMonday.status_code)
                raise Exception("Add to board failed.")
       #     time.sleep(secondsPause)
            return(responseMonday)
        monday()

        def exception():
            totalBillHoursList = clockify()
            valueExtractSecondsList = []
            totalBillSecondsList = [int(x*3600) for x in totalBillHoursList]

            columnIdsCheck = [columnId[0], columnId[1], columnId[2],
                              columnId[3], columnId[4], columnId[5], columnId[6]]

            for cic in columnIdsCheck:
                query = f'''query($itemid:[Int], $columnid:[String]){{items(ids: $itemid){{column_values (ids: $columnid) {{ value }} }}}}'''
                vars = {'itemid': miil,
                        'columnid': cic
                        }

                payloadExceptionMonday = {'query': query, 'variables': vars}
                responseExceptionMonday = requests.post(
                    url=urlMonday, json=payloadExceptionMonday, headers=headersMonday)
                valueExtractTemp = responseExceptionMonday.json()

                try:
                    valueExtract = valueExtractTemp['data']['items'][0]['column_values'][0]['value']
                    fromString = json.loads(json.loads(valueExtract))
                    valueExtractSeconds = int(fromString*3600)
                    valueExtractSecondsList.append(valueExtractSeconds)
                except:
                    valueExtractSecondsList.append(0)
            listComparison = (totalBillSecondsList == valueExtractSecondsList)
            if listComparison is False:
                print(
                    "The value in the row with Monday.com Item ID: ", miil, " in column ", cic, " was different than the value received from Clockify")
            return(valueExtractSecondsList)
        exception()


financeDetail()
