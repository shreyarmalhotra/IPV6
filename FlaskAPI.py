import os
import main
import pandas as pd
from flask import Flask, redirect, url_for, request, jsonify, render_template, make_response

# create the Flask application
app = Flask(__name__)


@app.route('/all_info/<name>')
def success(name):
    """
    Once "Get All Info" has been selected, this function redirects
    the user to a webpage that displays all of the requested information,
    ip address, hostname, pingability, open ports.
    :return: rendered info.html file specific for "Get All Info" button
    """
    names = name.split(',')
    global value
    value = main.multi_thread(names, main.threadForSingleAddress)
    kind = "Find All Info"
    global columns
    columns = ['Input', 'IP Address', 'Hostname', 'Pingable', 'Open Ports']
    return render_template('info.html', name=names, value=value, kind=kind, iterate=range(len(names)), columns=columns)


@app.route('/ip_address_and_hostname/<name>')
def address(name):
    """
    Once "IP Address / Hostname" has been selected, this function redirects
    the user to a webpage that displays the ip address and hostname, assuming
    valid input.
    :return: rendered info.html file specific for "IP Address / Hostname" button
    """
    names = name.split(',')
    global value
    value = main.multi_thread(names, main.getNameAndAddress)
    kind = 'IP Address and Hostname Lookup'
    global columns
    columns = ['Input', 'IP Address', 'Hostname']
    return render_template('info.html', name=names, value=value, kind=kind, iterate=range(len(names)), columns=columns)


@app.route('/pingable/<name>')
def do_ping(name):
    """
    Once "Pingable?" has been selected, this function redirects
    the user to a webpage that displays whether or not the input
    is pingable.
    :return: rendered info.html file specific for "Pingable?" button
    """
    names = name.split(',')
    global value
    value = main.multi_thread(names, main.pingable)
    kind = 'Check Pingability'
    global columns
    columns = ['Input', 'Pingable']
    return render_template('info.html', name=names, value=value, kind=kind, iterate=range(len(names)), columns=columns)


@app.route('/open_ports/<name>')
def ports(name):
    """
    Once "Open Ports" has been selected, this function redirects
    the user to a webpage that displays all of the open ports for
    the given input, assuming the host is pingable.
    :return: rendered info.html file specific for "Open Ports" button
    """
    names = name.split(',')
    global value
    value = main.multi_thread(names, main.check_ports)
    kind = 'Check Open Ports'
    global columns
    columns = ['Input', 'Open Ports']
    return render_template('info.html', name=names, value=value, kind=kind, iterate=range(len(names)), columns=columns)


@app.route('/')
def load_index():
    """
    Upon visiting http://126.0.0.1:3000, this will
    render index.html without any error messages.

    :return: rendered index.html file for render
    """
    return render_template('index.html', error='')


@app.route('/index', methods=['POST'])
def index():
    """
    When http://127.0.0.6:3000/index is visited, the user may input an ip address or hostname.
    Upon pressing one of the four buttons, this function will receive the inputted information
    and then redirect the user to the appropriate URL.
    :return: URL for redirecting
    """
    user = request.form['nm']
    addresses = user.split(',')
    valid = True
    for addr in addresses:
        output_stream = os.popen("nslookup " + addr)
        server_address = output_stream.read()
        if 'Name' not in server_address:
            valid = False

    if valid:
        if request.form.get('all'):
            return redirect(url_for('success', name=user))
        elif request.form.get('addr'):
            return redirect(url_for('address', name=user))
        elif request.form.get('ping'):
            return redirect(url_for('do_ping', name=user))
        elif request.form.get('port'):
            return redirect(url_for('ports', name=user))
    else:
        return render_template('index.html', error='Error: Please try again with a valid address or hostname')


@app.route('/receiver', methods=['POST'])
def receiver():
    """
    Whenever a user selects "Download csv" or "Download json", that action will
    be returned here. The user will then be redirected to the corresponding URL
    for downloading their file.
    :return: URL for redirecting
    """
    if request.form.get('csv'):
        return redirect(url_for('download_csv'))
    elif request.form.get('json'):
        return redirect(url_for('download_json'))


def make_df():
    """
    Using the requested user values and the appropriate column names, a dataframe
    is created.
    :return: pandas DataFrame
    """
    return pd.DataFrame(value, columns=columns[1:])


@app.route('/csv')
def download_csv():
    """
    Upon being redirected here, a csv file with the requested information will
    be created and then downloaded.
    :return: Downloadable csv file
    """
    response = make_response(make_df().to_csv())
    cd = 'attachment; filename=download.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route('/json')
def download_json():
    """
    Upon being redirected here, a json file with the requested information will
    be created and then downloaded.
    :return: Downloadable json file
    """
    response = make_response(jsonify(make_df().to_json()))
    cd = 'attachment; filename=download.json'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/json'
    return response


if __name__ == '__main__':
    # run the Flask App
    app.run(host='127.0.0.6', port=3000)