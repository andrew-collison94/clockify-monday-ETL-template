import requests
import json
import requests.models
from itertools import chain
import config

# Name of linked Monday.com board
boardName = "Sample Board Name"
boardId = config.overviewDashboardMondayBoardID  # Monday.com Board ID
columnId = config.overviewDashboardMondayColumnID  # List of Monday.com columns that will be updated
expectedRowCount = 12  # Count of every row on board in Monday.com at the time of setup
workspace_id = config.workspaceConfigClockify  # Clockify Workspace ID
startdate = ["2021-10-01T00:00:00.000", "2021-11-01T00:00:00.000", "2021-12-01T00:00:00.000", "2022-01-01T00:00:00.000", "2022-02-01T00:00:00.000", "2022-03-01T00:00:00.000",
             "2022-04-01T00:00:00.000"]  # List of start dates formatted like: "2021-05-01T00:00:00.000" for Clockify query (used for rows that iterate to diplay a monthly total)
enddate = ["2021-10-31T23:59:59.999", "2021-11-30T23:59:59.999", "2021-12-31T23:59:59.999", "2022-01-31T23:59:59.999", "2022-02-28T23:59:59.999", "2022-03-31T23:59:59.999",
           "2022-04-30T23:59:59.999"]  # List of end dates formatted like: "2021-05-31T23:59:59.999" for Clockify query (used for rows that iterate to diplay a monthly total)
# Start date formatted like: "2021-05-01T00:00:00.000" for Clockify query (only used for High level, project total hours)
highLevelSD = "2021-01-01T00:00:00.000"
# End date formatted like: "2021-05-31T23:59:59.999" for Clockify query (only used for High level, project total hours)
highLevelED = "2023-12-31T23:59:59.999"
# High level Monday.com board ID (only used for High level, project total hours)
hLBoardId = 0000000000000
# High level Monday.com item ID (only used for High level, project total hours)
hLItemId = 0000000000000
# Totals Monday.com item ID (Project total hours, the last item of the overview board)
totalsItemId = 0000000000000
# High level Monday.com column ID ((only used for High level, project total hours)
hLColumnId = "numbers"
# Clockify Project ID: Project Name
project_id = "000000000000000000000000"
# Admin API key linked to user: Name of API Admin
apiKeyClockify = config.apiConfigClockify

urlClockify = "https://reports.api.clockify.me/v1/workspaces/{0}/reports/summary".format(
    workspace_id)
headersClockify = {"X-Api-Key": apiKeyClockify,
                   "Content-Type": "application/json"}

apiKeyMonday = config.apiConfigMonday
urlMonday = 'https://api.monday.com/v2'
headersMonday = {"Authorization": apiKeyMonday}
# Clockify Task IDs. Each group in [] represents a row in Monday.com organized from top to bottom
clockifyTaskIdList = config.overviewDashboardClockifyTaskID
# Monday Item IDs. Each ID represents a row, organized from top to bottom
mondayItemIdList = config.overviewDashboardMondayItemID
# clockifyTaskIdList and mondayItemIdList must contain the same amount of values
if len(mondayItemIdList) != len(clockifyTaskIdList):
    print("The number of tasks in Clockify and items in Monday do not match up, please contact an administrator")
    raise PermissionError(
        "Clockify task list and Monday item list do not contain the same amount of items")


def highLevelClockify():
    payloadClockify = {
        "dateRangeStart": highLevelSD,
        "dateRangeEnd": highLevelED,
        "summaryFilter": {
            "groups": ["PROJECT", "TASK"]},
        "projects": {
            "ids": [project_id]}
    }

    responseClockify = requests.post(
        urlClockify, headers=headersClockify, data=json.dumps(payloadClockify))
    timeExtract = responseClockify.json()
    try:
        totalBillSeconds = timeExtract['totals'][0]['totalBillableTime']
        totalBillHours = totalBillSeconds/3600

    except:
        totalBillHours = 0
    if responseClockify.status_code == 401:
        print('Status: ', responseClockify.status_code)
        raise PermissionError(
            "The API key for Clockify appears to be expired.")
    if responseClockify.status_code != 200:
        print('Status: ', responseClockify.status_code)
        raise Exception("Query failed.")

    return(totalBillHours)


highLevelClockify()


def highLevelMonday():
    totalBillHours = highLevelClockify()
    varStringify = {
        hLColumnId: totalBillHours}

    query = f'''mutation ($boardid: Int!, $itemid: Int!, $billable: JSON!) \
    {{change_multiple_column_values (board_id: $boardid, item_id: $itemid, column_values: $billable) {{ id }} }}'''

    vars = {'boardid': hLBoardId,
            'itemid': hLItemId,
            'billable': json.dumps(varStringify)
            }
    payloadMonday = {'query': query, 'variables': vars}
    responseMonday = requests.post(
        url=urlMonday, json=payloadMonday, headers=headersMonday)  # make request

    return(responseMonday)


highLevelMonday()