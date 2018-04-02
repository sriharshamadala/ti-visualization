#!/usr/bin/python
import sys
sys.path.append('./google-visualization-python')
import gviz_api
from datetime import datetime, timedelta
# Needed if data is coming from a json file.
import json 

page_template = """
<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load("current", {packages:["timeline"]});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var container = document.getElementById('timeline1.0');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();
        %(jscode)s
        chart.draw(dataTable);
        var options = {
            title: 'Projects Timeline',
            // This line makes the entire category's tooltip active.
            focusTarget: 'category',
            // Use an HTML tooltip.
            tooltip: { isHtml: true }
          };
      }
    </script>
  </head>
  <body>
    <div id="timeline1.0" style="height: 800px;"></div>
  </body>
</html>
"""

def CreateCustomHtmlContent(project_phase):
    ret_string = '<div> <table>';
    is_grey = True
    task_list = project_phase['taskDescription']
    for ii in xrange(len(task_list)):
        task = task_list[ii]
        is_weekday = datetime.weekday(project_phase['taskDate'][ii])
        time_spent = project_phase['taskHours'][ii]
        if task is not None:
            task = "[" + "{0:05.2f}".format(round(time_spent,2)) + "] " + task
            if is_grey:
                if (is_weekday==5) or (is_weekday==6):
                    ret_string = ret_string + '<tr bgcolor="#D6D6D6"><td><font FACE="calibri" size=2 color="red">' + task + '</font></td></tr>'
                else:
                    ret_string = ret_string + '<tr bgcolor="#D6D6D6"><td><font FACE="calibri" size=2>' + task + '</font></td></tr>'
                is_grey = False
            else:
                if (is_weekday==5) or (is_weekday==6):
                    ret_string = ret_string + '<tr bgcolor="white"><td><font FACE="calibri" size=2 color="red">' + task + '</font></td></tr>'
                else:
                    ret_string = ret_string + '<tr bgcolor="white"><td><font FACE="calibri" size=2>' + task + '</font></td></tr>'
                is_grey = True
    ret_string = ret_string + '</table></div>'
    return ret_string;

def main():
    time_tracker_file = open(sys.argv[1])
    time_tracker_str = time_tracker_file.read()
    time_tracker_data = json.loads(time_tracker_str)["work"]

    # Any project discontinuity greater than threshold gets broken down.
    discontinuity_threshold = 5

    # Creating a project id (some unique val) and project name dictionary
    my_projects = {}
    curr_project_id = 1;
    for time_entry in time_tracker_data:
        # Storing timestamps as datetime objects
        time_entry['start'] = datetime.strptime(time_entry['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if ('end' in time_entry):
            time_entry['end'] = datetime.strptime(time_entry['end'], "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            # If missing end, added a standard 8 hour workday
            time_entry['end'] = time_entry['start'] + timedelta(hours=8)
        # If missing notes, add an empty string. 
        if ('notes' not in time_entry):
            time_entry['notes'] = [u'']
        # IF multiple notes, merge into single string.
        temp_string = ''
        for note in time_entry['notes']:
            temp_string = temp_string + ' ' + note
        time_entry['notes'] = [temp_string]
        if time_entry['name'] not in my_projects:
            my_projects[time_entry['name']] = curr_project_id
            curr_project_id += 1

    # Store projects in phases.
    my_projects_in_phases = {}
    for time_entry in time_tracker_data:
        current_pid = my_projects[time_entry['name']]
        if current_pid in my_projects_in_phases.keys():
            found_task = False
            for tmp_dict in my_projects_in_phases[current_pid]:
                if (((time_entry['start']-tmp_dict['start']).days > -discontinuity_threshold) and ((time_entry['end']-tmp_dict['end']).days < discontinuity_threshold)):
                    tmp_dict['taskDescription'] += time_entry['notes']
                    tmp_dict['taskDate'].append(time_entry['start'])
                    tmp_dict['taskHours'].append(abs(time_entry['end']-time_entry['start']).seconds/3600.0)
                    # Adjust the start or end dates.
                    if (time_entry['start'] < tmp_dict['start']):
                        tmp_dict['start'] = time_entry['start']
                    elif (time_entry['end'] > tmp_dict['end']):
                        tmp_dict['end'] = time_entry['end']
                    found_task = True
                    break
            if not found_task:
                tmp_dict = {}
                tmp_dict['projectName'] = time_entry['name']
                tmp_dict['start'] = time_entry['start']
                tmp_dict['end'] = time_entry['end']
                tmp_dict['taskDate'] = []
                tmp_dict['taskHours'] = []
                tmp_dict['taskDescription'] = time_entry['notes']
                tmp_dict['taskDate'].append(time_entry['start'])
                tmp_dict['taskHours'].append(abs(time_entry['end']-time_entry['start']).seconds/3600.0)
                my_projects_in_phases[current_pid].append(tmp_dict)
        else:
            # process the start and end 
            my_projects_in_phases[current_pid] = []
            tmp_dict = {}
            tmp_dict['projectName'] = time_entry['name']
            tmp_dict['start'] = time_entry['start']
            tmp_dict['end'] = time_entry['end']
            tmp_dict['taskDate'] = []
            tmp_dict['taskHours'] = []
            tmp_dict['taskDescription'] = time_entry['notes']
            tmp_dict['taskDate'].append(time_entry['start'])
            tmp_dict['taskHours'].append(abs(time_entry['end']-time_entry['start']).seconds/3600.0)
            my_projects_in_phases[current_pid].append(tmp_dict)


    # Adding columns to dataTable
    description = {"projectId": ("string", "Project ID"),
             "projectName": ("string", "Project Name"),
             "description": ("string", "description", {'role':'tooltip', 'html':'true'}),
             "start": ("date", "Start"),
             "end": ("date", "End")}

    # Adding rows to dataTable
    data = []
    for tmp in my_projects_in_phases.keys():
        for project_phase in my_projects_in_phases[tmp]:
            tmp_row = {}
            tmp_row['projectId'] = tmp
            tmp_row['projectName'] = project_phase['projectName']
            tmp_row['description'] = CreateCustomHtmlContent(project_phase)
            tmp_row['start'] = project_phase['start']
            tmp_row['end'] = project_phase['end']
            data.append(tmp_row)

    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Creating a JavaScript code string
    jscode = data_table.ToJSCode("dataTable",columns_order=("projectId", "projectName", "description", "start", "end"))

    # Putting the JS code and JSon string into the template
    print page_template % vars()

if __name__ == "__main__":
    main()
