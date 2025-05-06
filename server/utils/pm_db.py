from datetime import datetime
from datetime import timedelta
import pymysql 
pymysql.install_as_MySQLdb()
import MySQLdb as mdb

class PMDB:
    """
    Module which provides PM DB access.

    It contains knowledge of the DB schema and maps higher level
    domain models into DB structures that match the DB schema.
    """
    db_host="127.0.0.1"
    db_port=3310
    db_user="root"
    db_pass=""
    db="pm"
    
    def __init__(self, db_host, db_port, db_user, db_pass, db, logger):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db = db
        self.logger = logger


    def get_db_connection(self):
        self.logger.debug("Connecting: %s:%s %s", self.db_host,self.db_port, self.db_user)
        #print("PMDB Connecting:", self.db_host,self.db_port, self.db_user)
        con = mdb.connect(host=self.db_host, port=self.db_port, user=self.db_user, passwd=self.db_pass, db=self.db, charset=None)
        #con.set_character_set('utf8')
        #print("PMDB Connection:", con)
        con.autocommit(True)
        return con
    
    def query_list1(self, query):
        self.logger.info("PMDB:QUERY_LIST1:%s", query)
        
        con = self.get_db_connection()
        #self.logger.debug("query_list: " + query + "\n" + str(query_values))
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query)
        return cur.fetchall()
        
    def query_list(self, query, query_values):
        self.logger.info("PMDB:QUERY_LIST:%s %s", query, query_values)

        con = self.get_db_connection()
        #self.logger.debug("query_list: " + query + "\n" + str(query_values))
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query, query_values)
        return cur.fetchall()
        
    def query_one(self, query, values):
        #self.logger.debug("query_one: " + query + " - " + str(values))
        self.logger.info("PMDB:QUERY_ONE:%s %s", query,values)
        con = self.get_db_connection()
    
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute(query, values)
        return cur.fetchone()

    def update(self, query):
        con = self.get_db_connection()
        self.logger.warn("PMDB:UPDATE:%s", query)
        cur = con.cursor()
        cur.execute(query)
        #con.commit()
    
    def update2(self, query, values):
        con = self.get_db_connection()
        self.logger.warn("PMDB:UPDATE2:%s | %s", query, values)
        cur = con.cursor()
        cur.execute(query, values)
        #con.commit()

    def delete(self, query):
        con = self.get_db_connection()
        self.logger.warn("PMDB:DEL:%s", query)
        cur = con.cursor()
        cur.execute(query)
        #con.commit()

    def insert(self, query, values):
        """Returns the ID from the DB cursor"""
        #self.logger.debug("insert: " + query + "\n" + str(values))
        self.logger.warn("PMDB:INSERT:%s %s", query, values)
        try:
            con = self.get_db_connection()
            cur = con.cursor()
            cur.execute(query, values)
            #return cur.fetchall()
        except pymysql.Error as e:
            self.logger.error("PMDB:insert:%s %s %s %s %s",query, values, e.args[0], e.args[1], e)
        #con.commit()
        #return cur.lastrowid
        
    def call_proc(self, query):
        
        con = self.get_db_connection()
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.callproc(query)
        return cur.fetchall()
        
    def call_proc2(self, query, query_values):
        
        con = self.get_db_connection()
        self.logger.warn("PMDB:SP:%s %s", query, values)
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.callproc(query, query_values)
        return cur.fetchall()
                