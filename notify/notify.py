# Notify plugin
""" Trac - Virtual planner plugin; each trac instance will use this to 
ping the central planner"""

import urllib2
import base64
import time

from trac.core import *
from trac.env import *
from trac.ticket.api import *

class Logger:
    """ Trivial debug script - writes messages out to /tmp/notify.debug """
    filename = '/tmp/notify.debug'
    log_file = None
    
    def debug(self, message):
        """ string message - what to write out to filename """
        self.log_file = open(self.filename, 'a')
        self.log_file.write(str(message) + "\n")
        self.log_file.flush()
        self.log_file.close()

class Notify(Component):
    """ Class to update a central virtual planner instance with changes """
    implements(ITicketChangeListener)
    logger = None
    
    def __init__(self):
        """ Initialization ... You will need to change self.path!"""
        self.logger = Logger()
        self.logger.debug('__init__()')
        self.path = 'https://www.example.com/planner/board/ping/'
        self.logger.debug('Notification target: ' + self.path)

    def ticket_deleted(self, ticket):
        """ Callback for ticket deletion """
        self.logger.debug('ticket_deleted(' + str(ticket) + ')')
        self.build_url(ticket, 'deleted')

    def ticket_created(self, ticket):
        """ callback for ticket creation """
        self.logger.debug('ticket_created(' + str(ticket) + ')')
        self.build_url(ticket, 'created')

    def ticket_changed(self, ticket, comment, author, old_values):
        """ callback for ticket change """
        self.logger.debug('ticket_changed(%s, %s, %s, %s)' % 
                (str(ticket), str(comment), str(author), str(old_values)))
        self.build_url(ticket, 'changed', comment, author)

    def build_url(self, ticket, action, comment = '', author = ''):
        """ Utility function for preparing and issuing the http request 
        to the remote virtual planner server """
        self.logger.debug('build_url(%s, %s, %s, %s)' % 
                (str(ticket), str(action), str(comment), str(author)))
        id = str(ticket.id)
        hours = ticket.values['hours']
        if hours == '':
            hours = 0
        
        try:
            total_hours = ticket.values['totalhours']
            if total_hours == '':
                total_hours = 0
        except KeyError:
            total_hours = 0
        
        data_dictionary = {
                'project': self.env.project_name,
                'owner': ticket.values['owner'],
                'type': ticket.values['type'],
                'status': ticket.values['status'],
                'title': ticket.values['summary'],
                'desc': ticket.values['description'],
                'total_hours': str(float(total_hours) + float(hours)),
                'estimated_hours': ticket.values['estimatedhours'],
                'ticket_url': self.env.abs_href.ticket(id),
               }
        # If it was a change, we can get some extra data.
        if comment != '' and author != '':
            data_dictionary['comment'] = str(comment)
            data_dictionary['author'] = str(author)
            
            # Get a database connection and find the latest change 
            # for this ticket.
            dbase = ticket.env.get_db_cnx()
            if dbase:
                cursor = dbase.cursor()
                sql = "SELECT time, newvalue FROM ticket_change WHERE field = 'hours' AND ticket=%s" % id
                cursor.execute(sql)
                row = cursor.fetchone()
                if row != None :
                    data_dictionary['change_time'] = str(row[0])
                    data_dictionary['change_hours'] = str(row[1])
                else:
                    self.logger.debug("Couldn't get database connection, or time field not changed ")
        
        data = 'trac_id=' + id + '&action=' + action
        for datum in data_dictionary:
            data = data + '&' + datum + '=' + data_dictionary[datum].encode('utf-8').replace('&', '%26')
        self.logger.debug('Data: ' + data)
        result = self.open_page(data)
        self.logger.debug('Result: %r' % result)
    def open_page(self, data):
        """ Performs the actual http request; 
        
        Tries 3 times if it gets a non 200 http status returned;
        2 second sleep between tries;
        Supports/assumes http basic authentication, if this isn't the case in your 
        environment you'll need to change the below. """

        self.logger.debug('open_page(' + str(data) + ')')
        username = 'planningboard'
        password = 'xxx'
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        authheader = "Basic %s" % base64string
        
        request = urllib2.Request(self.path)
        request.add_header("Authorization", authheader)
        request.add_data(data)
        i = 0
        success = False
        while i < 4 and not success :
            try:
                result = urllib2.urlopen(request)
                self.logger.debug('Planner ping request: OK')
                success = True
            except urllib2.URLError, ex:
                self.logger.debug("Unable to update virtual-planning board - Error: %s, Attempt: %d " % (str(ex), i))
                i += 1
                time.sleep(2)
        if i >= 3 and not success:
            self.logger.debug("Failed to update virtual planning board \
                    tried 3 times... giving up")
            return 'Error: Could not connect' + str(ex)
        return result
